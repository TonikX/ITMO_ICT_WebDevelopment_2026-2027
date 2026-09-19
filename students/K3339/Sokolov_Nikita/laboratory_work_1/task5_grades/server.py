from __future__ import annotations

from collections import defaultdict
from urllib.parse import parse_qs
import socket

HOST = "127.0.0.1"
PORT = 8085
BUFFER_SIZE = 8192

grades: dict[str, list[str]] = defaultdict(list)


def read_http_request(conn: socket.socket) -> tuple[str, str, dict[str, str], bytes]:
    chunks: list[bytes] = []
    while b"\r\n\r\n" not in b"".join(chunks):
        piece = conn.recv(BUFFER_SIZE)
        if not piece:
            break
        chunks.append(piece)
    raw = b"".join(chunks)
    header_part, _, body = raw.partition(b"\r\n\r\n")
    header_text = header_part.decode("utf-8", errors="replace")
    lines = header_text.split("\r\n")
    request_line = lines[0] if lines else "GET / HTTP/1.1"
    method, path, *_ = request_line.split(" ")

    headers: dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    content_length = int(headers.get("content-length", "0") or "0")
    while len(body) < content_length:
        body += conn.recv(BUFFER_SIZE)

    return method.upper(), path, headers, body[:content_length]


def render_grades_page(message: str = "") -> str:
    rows = []
    for subject in sorted(grades):
        marks = ", ".join(grades[subject])
        rows.append(f"<tr><td>{subject}</td><td>{marks}</td></tr>")

    table_body = (
        "\n".join(rows)
        if rows
        else '<tr><td colspan="2">Пока нет оценок</td></tr>'
    )
    notice = f'<p class="notice">{message}</p>' if message else ""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Журнал оценок</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; background: #f4f7f2; color: #222; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #99a; padding: 0.5rem 0.75rem; text-align: left; }}
    th {{ background: #dfe8d8; }}
    form {{ display: grid; gap: 0.5rem; max-width: 320px; }}
    input, button {{ padding: 0.4rem 0.5rem; font: inherit; }}
    .notice {{ color: #1b5e20; }}
  </style>
</head>
<body>
  <h1>Журнал оценок</h1>
  {notice}
  <h2>Добавить оценку</h2>
  <form method="POST" action="/">
    <label>Дисциплина <input name="subject" required></label>
    <label>Оценка <input name="grade" required></label>
    <button type="submit">Сохранить</button>
  </form>
  <h2>Все оценки (группировка по предмету)</h2>
  <table>
    <thead><tr><th>Дисциплина</th><th>Оценки</th></tr></thead>
    <tbody>
      {table_body}
    </tbody>
  </table>
</body>
</html>"""


def http_response(status: str, body: str, content_type: str = "text/html; charset=utf-8") -> bytes:
    payload = body.encode("utf-8")
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(payload)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + payload


def handle_request(method: str, body: bytes) -> bytes:
    if method == "POST":
        form = parse_qs(body.decode("utf-8", errors="replace"))
        subject = (form.get("subject") or [""])[0].strip()
        grade = (form.get("grade") or [""])[0].strip()
        if subject and grade:
            grades[subject].append(grade)
            page = render_grades_page(f"Добавлено: {subject} → {grade}")
        else:
            page = render_grades_page("Нужно указать дисциплину и оценку")
        return http_response("200 OK", page)

    if method == "GET":
        return http_response("200 OK", render_grades_page())

    return http_response("405 Method Not Allowed", "<h1>405 Method Not Allowed</h1>")


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"Журнал оценок: http://{HOST}:{PORT}/")

        while True:
            conn, address = server.accept()
            with conn:
                try:
                    method, path, _headers, body = read_http_request(conn)
                    print(f"{address}: {method} {path}")
                    conn.sendall(handle_request(method, body))
                except Exception as exc:
                    print(f"Ошибка обработки {address}: {exc}")
                    conn.sendall(http_response("500 Internal Server Error", "<h1>500</h1>"))


if __name__ == "__main__":
    main()
