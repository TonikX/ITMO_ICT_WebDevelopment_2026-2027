import socket
from pathlib import Path
from urllib.parse import parse_qs
from html import escape

grades = {}


def make_page():
    html_path = Path(__file__).parent / "index.html"
    page = html_path.read_text(encoding="utf-8")

    rows = ""

    for subject, marks in grades.items():
        marks_text = ", ".join(map(str, marks))
        rows += (
            f"<tr><td>{escape(subject)}</td>"
            f"<td>{marks_text}</td></tr>"
        )

    return page.replace("{{rows}}", rows)


def send_response(connection, status, text, extra_headers=""):
    body = text.encode("utf-8")

    headers = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        f"{extra_headers}"
        "\r\n"
    )

    connection.sendall(headers.encode("utf-8") + body)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8001))
server.listen(5)

print("Журнал доступен: http://127.0.0.1:8001")

while True:
    connection, address = server.accept()

    try:
        request = b""

        while b"\r\n\r\n" not in request:
            data = connection.recv(1024)

            if not data:
                break

            request += data

        if b"\r\n\r\n" not in request:
            continue

        headers_data, body = request.split(b"\r\n\r\n", 1)

        lines = headers_data.decode("iso-8859-1").split("\r\n")
        method, path, version = lines[0].split()

        headers = {}

        for line in lines[1:]:
            key, value = line.split(":", 1)
            headers[key.lower()] = value.strip()

        content_length = int(headers.get("content-length", "0"))

        while len(body) < content_length:
            data = connection.recv(1024)

            if not data:
                break

            body += data

        if len(body) < content_length:
            send_response(
                connection,
                "400 Bad Request",
                "Неполный запрос"
            )

        elif path != "/":
            send_response(
                connection,
                "404 Not Found",
                "Страница не найдена"
            )

        elif method == "GET":
            send_response(connection, "200 OK", make_page())

        elif method == "POST":
            form = parse_qs(body[:content_length].decode("utf-8"))

            subject = form.get("subject", [""])[0].strip()
            grade = int(form.get("grade", ["0"])[0])

            if not subject or grade < 1 or grade > 5:
                send_response(
                    connection,
                    "400 Bad Request",
                    "Введите дисциплину и целую оценку от 1 до 5"
                )

            else:
                if subject not in grades:
                    grades[subject] = []

                grades[subject].append(grade)

                send_response(
                    connection,
                    "303 See Other",
                    "",
                    "Location: /\r\n"
                )

        else:
            send_response(
                connection,
                "405 Method Not Allowed",
                "Метод не поддерживается",
                "Allow: GET, POST\r\n"
            )

    except (ValueError, UnicodeError):
        send_response(
            connection,
            "400 Bad Request",
            "Некорректные данные"
        )

    except OSError:
        pass

    finally:
        connection.close()