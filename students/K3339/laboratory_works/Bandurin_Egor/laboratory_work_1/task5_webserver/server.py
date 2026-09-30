import socket
from html import escape
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8081
BUFFER_SIZE = 1024

grades: dict[str, list[str]] = {}


def read_http_request(connection: socket.socket) -> tuple[str, str, bytes]:
    data = b""

    while b"\r\n\r\n" not in data:
        chunk = connection.recv(BUFFER_SIZE)
        if not chunk:
            raise ConnectionError("Клиент отключился до отправки заголовков")
        data += chunk

    headers_data, _, body = data.partition(b"\r\n\r\n")
    header_lines = headers_data.decode("iso-8859-1").split("\r\n")
    method, path, _ = header_lines[0].split(" ", 2)

    headers: dict[str, str] = {}
    for line in header_lines[1:]:
        if ":" in line:
            name, value = line.split(":", 1)
            headers[name.lower()] = value.strip()

    content_length = int(headers.get("content-length", "0"))
    while len(body) < content_length:
        chunk = connection.recv(BUFFER_SIZE)
        if not chunk:
            break
        body += chunk

    return method, path.partition("?")[0], body[:content_length]


def make_http_response(status: str, body: str) -> bytes:
    body_bytes = body.encode("utf-8")
    headers = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body_bytes


def build_page(message: str = "") -> str:
    rows = ""
    for discipline, discipline_grades in sorted(grades.items()):
        marks = ", ".join(escape(mark) for mark in discipline_grades)
        rows += (
            "<tr>"
            f"<td>{escape(discipline)}</td>"
            f"<td>{marks}</td>"
            f"<td>{len(discipline_grades)}</td>"
            "</tr>"
        )

    if rows:
        journal = (
            "<table>"
            "<thead><tr><th>Дисциплина</th><th>Оценки</th><th>Количество</th></tr></thead>"
            f"<tbody>{rows}</tbody>"
            "</table>"
        )
    else:
        journal = "<p>Оценок пока нет.</p>"

    message_html = f'<p class="message">{escape(message)}</p>' if message else ""

    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Журнал оценок</title>
    <style>
      body {{ max-width: 760px; margin: 40px auto; padding: 0 20px; font-family: sans-serif; }}
      form {{ display: grid; gap: 12px; max-width: 360px; }}
      input, button {{ padding: 8px; font: inherit; }}
      table {{ width: 100%; margin-top: 24px; border-collapse: collapse; }}
      th, td {{ padding: 10px; border: 1px solid #999; text-align: left; }}
      .message {{ color: #176b32; }}
    </style>
  </head>
  <body>
    <h1>Журнал оценок</h1>
    {message_html}
    <form method="post" action="/">
      <label>Дисциплина <input name="discipline" required></label>
      <label>Оценка <input name="grade" required></label>
      <button type="submit">Добавить оценку</button>
    </form>
    <h2>Все оценки</h2>
    {journal}
  </body>
</html>"""


def handle_request(method: str, path: str, body: bytes) -> bytes:
    if path != "/":
        return make_http_response(
            "404 Not Found",
            '<h1>404 — страница не найдена</h1><p><a href="/">На главную</a></p>',
        )

    if method == "GET":
        return make_http_response("200 OK", build_page())

    if method == "POST":
        fields = parse_qs(body.decode("utf-8"))
        discipline = fields.get("discipline", [""])[0].strip()
        grade = fields.get("grade", [""])[0].strip()

        if not discipline or not grade:
            return make_http_response(
                "400 Bad Request",
                build_page("Необходимо заполнить оба поля."),
            )

        grades.setdefault(discipline, []).append(grade)
        return make_http_response(
            "200 OK",
            build_page(f"Добавлена оценка {grade} по дисциплине «{discipline}»."),
        )

    return make_http_response(
        "405 Method Not Allowed",
        "<h1>Метод не поддерживается</h1>",
    )


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Grade server is running at http://{HOST}:{PORT}")

        try:
            while True:
                connection, address = server_socket.accept()
                with connection:
                    try:
                        method, path, body = read_http_request(connection)
                        print(f"{address}: {method} {path}")
                        response = handle_request(method, path, body)
                        connection.sendall(response)
                    except (ConnectionError, UnicodeError, ValueError) as error:
                        print(f"{address}: request error: {error}")
        except KeyboardInterrupt:
            print("\nGrade server stopped")


if __name__ == "__main__":
    main()
