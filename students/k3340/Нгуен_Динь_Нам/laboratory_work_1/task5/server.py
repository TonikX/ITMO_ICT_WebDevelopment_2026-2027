import json
import socket
from html import escape
from pathlib import Path
from urllib.parse import parse_qs

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "grades.json"

grades = {}

if DATA_FILE.exists():
    content = DATA_FILE.read_text(encoding="utf-8-sig").strip()

    if content:
        grades = json.loads(content)

normalized_grades = {}

for subject, records in grades.items():
    subject_key = subject.strip().casefold()
    normalized_grades.setdefault(subject_key, []).extend(records)

grades = normalized_grades

def make_page():
    rows = ""

    for subject, records in grades.items():
        for record in records:
            if not isinstance(record, dict):
                record = {"grade": record}

            student_id = escape(record.get("student_id", "") or "—")
            student_name = escape(record.get("student_name", "") or "—")
            subject_name = escape(subject)
            mark = escape(str(record["grade"]))
            rows += (
                "<tr>"
                f"<td>{student_id}</td>"
                f"<td>{student_name}</td>"
                f"<td>{subject_name}</td>"
                f"<td>{mark}</td>"
                "</tr>"
            )

    if not rows:
        rows = '<tr><td colspan="4">Добавьте первую оценку.</td></tr>'

    template = (BASE_DIR / "index.html").read_text(encoding="utf-8")

    return template.replace("{{rows}}", rows)

def read_request(connection):
    data = b""

    while b"\r\n\r\n" not in data:
        chunk = connection.recv(1024)

        if not chunk:
            raise ValueError("Incomplete request")

        data += chunk

    header, body = data.split(b"\r\n\r\n", 1)
    lines = header.decode("iso-8859-1").split("\r\n")
    method, path, version = lines[0].split()
    headers = {}

    for line in lines[1:]:
        name, value = line.split(":", 1)
        headers[name.lower()] = value.strip()

    length = int(headers.get("content-length", "0"))

    if length < 0 or "transfer-encoding" in headers:
        raise ValueError("Unsupported body")

    if method == "POST" and "content-length" not in headers:
        raise ValueError("Missing Content-Length")

    while len(body) < length:
        chunk = connection.recv(min(1024, length - len(body)))

        if not chunk:
            raise ValueError("Incomplete body")

        body += chunk

    return method, path, body[:length]

def send_response(connection, status, text="", content_type="text/html; charset=utf-8", location=""):
    body = text.encode("utf-8")

    headers = f"HTTP/1.1 {status}\r\n"
    headers += f"Content-Type: {content_type}\r\n"
    headers += f"Content-Length: {len(body)}\r\n"
    headers += "Connection: close\r\n"

    if location:
        headers += f"Location: {location}\r\n"

    headers += "\r\n"

    try:
        connection.sendall(headers.encode("ascii") + body)
    except OSError:
        print("Client disconnected before receiving.")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(10)
    server.settimeout(1.0)

    try:
        while True:
            try:
                connection, address = server.accept()
            except socket.timeout:
                continue

            with connection:
                connection.settimeout(5.0)

                try:
                    method, path, body = read_request(connection)

                    if method == "GET" and path == "/":
                        send_response(connection, "200 OK", make_page())

                    elif method == "GET" and path == "/style.css":
                        css = (BASE_DIR / "style.css").read_text(encoding="utf-8")
                        send_response(connection, "200 OK", css, content_type="text/css; charset=utf-8")

                    elif method == "POST" and path == "/grades":
                        fields = parse_qs(body.decode("utf-8"), errors="strict", keep_blank_values=True)
                        subject = fields.get("subject", [""])[0].strip().casefold()
                        grade = int(fields.get("grade", [""])[0])
                        student_name = fields.get("student_name", [""])[0].strip()
                        student_id = fields.get("student_id", [""])[0].strip()

                        if not subject or not 1 <= grade <= 5:
                            raise ValueError("Invalid subject or grade")

                        record = {"student_name": student_name, "student_id": student_id, "grade": grade}
                        updated = dict(grades)
                        updated[subject] = grades.get(subject, []) + [record]
                        temporary_file = DATA_FILE.with_suffix(".tmp")
                        temporary_file.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
                        temporary_file.replace(DATA_FILE)
                        grades[subject] = updated[subject]

                        send_response(connection, "303 See Other", location="/")

                    else:
                        send_response(connection, "404 Not Found", "<h1>Страница не найдена</h1>")

                except ValueError:
                    error_page = '<p>Укажите предмет и целую оценку от 1 до 5.</p><a href="/">Вернуться</a>'
                    send_response(connection, "400 Bad Request", error_page)

                except OSError as error:
                    print(error)
                    send_response(connection, "500 Internal Server Error", "<h1>Не удалось обработать запрос</h1>")

    except KeyboardInterrupt:
        print("\nServer stopped")