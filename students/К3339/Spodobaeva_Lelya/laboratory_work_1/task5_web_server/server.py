from pathlib import Path
from urllib.parse import parse_qs
import json
import socket


HOST = "127.0.0.1"
PORT = 5005
BUFFER_SIZE = 8192
DATA_FILE = Path(__file__).resolve().parent / "grades.json"


def load_grades():
    if not DATA_FILE.exists():
        return {}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_grades(grades):
    DATA_FILE.write_text(json.dumps(grades, ensure_ascii=False, indent=2), encoding="utf-8")


def add_grade(subject, grade):
    grades = load_grades()
    grades.setdefault(subject, []).append(grade)
    save_grades(grades)


def render_page(message=""):
    grades = load_grades()
    rows = []

    for subject, values in grades.items():
        values_text = ", ".join(values)
        rows.append(f"<tr><td>{subject}</td><td>{values_text}</td></tr>")

    table_body = "\n".join(rows) or "<tr><td colspan='2'>Оценок пока нет</td></tr>"

    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
    <style>
      body {{
        margin: 40px;
        font-family: Arial, sans-serif;
        line-height: 1.5;
      }}

      input, button {{
        display: block;
        margin: 8px 0 16px;
        padding: 8px;
        min-width: 260px;
      }}

      table {{
        border-collapse: collapse;
        margin-top: 24px;
      }}

      th, td {{
        border: 1px solid #999;
        padding: 8px 12px;
      }}
    </style>
  </head>
  <body>
    <h1>Журнал оценок</h1>
    <p>{message}</p>
    <form method="post" action="/grades">
      <label>
        Дисциплина
        <input name="subject" required>
      </label>
      <label>
        Оценка
        <input name="grade" required>
      </label>
      <button type="submit">Сохранить</button>
    </form>
    <table>
      <thead>
        <tr>
          <th>Дисциплина</th>
          <th>Оценки</th>
        </tr>
      </thead>
      <tbody>
        {table_body}
      </tbody>
    </table>
  </body>
</html>"""


def parse_request(raw_request):
    header_part, _, body = raw_request.partition("\r\n\r\n")
    lines = header_part.splitlines()
    if not lines:
        return "", "", {}, body

    method, path, *_ = lines[0].split()
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.lower()] = value.strip()
    return method, path, headers, body


def make_response(body, status="200 OK"):
    body_bytes = body.encode("utf-8")
    headers = [
        f"HTTP/1.1 {status}",
        "Content-Type: text/html; charset=utf-8",
        f"Content-Length: {len(body_bytes)}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("utf-8") + body_bytes


def receive_request(client_socket):
    request_data = b""

    while b"\r\n\r\n" not in request_data:
        chunk = client_socket.recv(BUFFER_SIZE)
        if not chunk:
            break
        request_data += chunk

    header_data, separator, body = request_data.partition(b"\r\n\r\n")
    headers_text = header_data.decode("utf-8", errors="ignore")
    content_length = 0

    for line in headers_text.splitlines()[1:]:
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break

    while separator and len(body) < content_length:
        chunk = client_socket.recv(BUFFER_SIZE)
        if not chunk:
            break
        body += chunk

    return (header_data + separator + body).decode("utf-8", errors="ignore")


def handle_request(raw_request):
    method, path, _, body = parse_request(raw_request)

    if method == "GET" and path == "/":
        return make_response(render_page())

    if method == "POST" and path == "/grades":
        form = parse_qs(body)
        subject = form.get("subject", [""])[0].strip()
        grade = form.get("grade", [""])[0].strip()

        if subject and grade:
            add_grade(subject, grade)
            return make_response(render_page("Оценка сохранена."))

        return make_response(render_page("Заполните дисциплину и оценку."), "400 Bad Request")

    return make_response("<h1>404 Not Found</h1>", "404 Not Found")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Сервер запущен: http://{HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                raw_request = receive_request(client_socket)
                print(f"Request from {client_address}: {raw_request.splitlines()[0] if raw_request else ''}")
                client_socket.sendall(handle_request(raw_request))


if __name__ == "__main__":
    main()
