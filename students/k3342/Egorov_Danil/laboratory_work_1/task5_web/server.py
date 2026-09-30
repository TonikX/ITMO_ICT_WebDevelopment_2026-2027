import html
import socket
from urllib.parse import parse_qs

HOST, PORT = "localhost", 8080

grades = {}


def build_response(status: str, body: str = "", extra_headers: str = "") -> bytes:
    body_bytes = body.encode("utf-8")
    headers = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"{extra_headers}"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body_bytes


def render_page() -> str:
    if grades:
        rows = "".join(
            f"<tr><td>{html.escape(subject)}</td>"
            f"<td>{', '.join(str(g) for g in marks)}</td></tr>"
            for subject, marks in grades.items()
        )
    else:
        rows = '<tr><td colspan="2">Оценок пока нет</td></tr>'
    return f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Журнал оценок</title></head>
<body>
    <h1>Журнал оценок</h1>
    <table border="1" cellpadding="6">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
    <h2>Добавить оценку</h2>
    <form method="POST" action="/">
        <input name="discipline" placeholder="Дисциплина" required>
        <input name="grade" type="number" min="0" max="100" placeholder="Оценка" required>
        <button type="submit">Сохранить</button>
    </form>
</body>
</html>"""


def read_request(conn):
    """Читает заголовки, затем ровно Content-Length байт тела. Возвращает (метод, путь, тело)."""
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    lines = head.decode("utf-8", errors="replace").split("\r\n")
    method, path, _ = lines[0].split(" ", 2)

    length = 0
    for line in lines[1:]:
        name, _, value = line.partition(":")
        if name.strip().lower() == "content-length":
            length = int(value.strip())
    while len(body) < length:
        chunk = conn.recv(4096)
        if not chunk:
            break
        body += chunk
    return method, path, body.decode("utf-8", errors="replace")


def handle(conn):
    req = read_request(conn)
    if req is None:
        return
    method, path, body = req
    print(f"{method} {path}")

    if path != "/":
        conn.sendall(build_response("404 Not Found", "<h1>404: страница не найдена</h1>"))
    elif method == "GET":
        conn.sendall(build_response("200 OK", render_page()))
    elif method == "POST":
        form = parse_qs(body)
        subject = form.get("discipline", [""])[0].strip()
        grade_text = form.get("grade", [""])[0].strip()
        if not subject or not grade_text.isdigit() or not 0 <= int(grade_text) <= 100:
            conn.sendall(build_response("400 Bad Request", "<h1>400: нужны дисциплина и оценка 0-100</h1>"))
        else:
            grades.setdefault(subject, []).append(int(grade_text))
            conn.sendall(build_response("303 See Other", extra_headers="Location: /\r\n"))
    else:
        conn.sendall(build_response("405 Method Not Allowed", "<h1>405</h1>"))


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Веб-сервер запущен: http://{HOST}:{PORT}")

while True:
    conn, addr = server_socket.accept()
    conn.settimeout(5)
    try:
        handle(conn)
    except (ValueError, OSError) as e:
        print(f"Ошибка обработки запроса: {e}")
    finally:
        conn.close()
