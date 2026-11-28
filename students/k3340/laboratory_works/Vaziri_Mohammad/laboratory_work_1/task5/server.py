"""Задание 5. Простой веб-сервер на socket.

POST /  — принимает дисциплину и оценку (form-urlencoded: discipline=...&grade=...)
          и добавляет оценку к дисциплине.
GET  /  — отдаёт HTML-страницу со всеми оценками и формой добавления.

Оценки хранятся сгруппированно: одна запись на дисциплину со списком оценок.
"""
import html
import socket
from urllib.parse import parse_qs

HOST, PORT = "127.0.0.1", 8085
grades: dict[str, list[str]] = {}                  # {"Математика": ["5", "4"], ...}


def parse_request(raw: bytes):
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("utf-8", errors="replace").split("\r\n")
    method, path, _ = lines[0].split(" ", 2)
    headers = {}
    for line in lines[1:]:
        key, _, value = line.partition(":")
        headers[key.strip().lower()] = value.strip()
    return method, path, headers, body


def read_full_request(conn: socket.socket) -> bytes:
    data = b""
    while b"\r\n\r\n" not in data:                   # сначала дочитываем заголовки
        chunk = conn.recv(4096)
        if not chunk:
            return data
        data += chunk
    _, _, headers, body = parse_request(data)
    need = int(headers.get("content-length", 0))
    while len(body) < need:                        # потом тело по Content-Length
        chunk = conn.recv(4096)
        if not chunk:
            break
        body += chunk
        data += chunk
    return data


def page() -> bytes:
    rows = "".join(
        f"<tr><td>{html.escape(d)}</td><td>{html.escape(', '.join(g))}</td></tr>"
        for d, g in grades.items()
    ) or '<tr><td colspan="2">Оценок пока нет</td></tr>'
    doc = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Оценки</title></head>
<body>
<h1>Оценки по дисциплинам</h1>
<table border="1" cellpadding="6">
<tr><th>Дисциплина</th><th>Оценки</th></tr>{rows}
</table>
<h2>Добавить оценку</h2>
<form method="POST" action="/">
  <input name="discipline" placeholder="Дисциплина" required>
  <input name="grade" placeholder="Оценка" required>
  <button type="submit">Сохранить</button>
</form>
</body></html>"""
    return doc.encode("utf-8")


def response(status: str, body: bytes = b"", extra: list[str] | None = None) -> bytes:
    headers = [f"HTTP/1.1 {status}", "Content-Type: text/html; charset=utf-8",
               f"Content-Length: {len(body)}", "Connection: close"] + (extra or [])
    return ("\r\n".join(headers) + "\r\n\r\n").encode("utf-8") + body


def handle(conn: socket.socket) -> None:
    raw = read_full_request(conn)
    if not raw:
        return
    method, path, _, body = parse_request(raw)
    if method == "GET" and path == "/":
        conn.sendall(response("200 OK", page()))
    elif method == "POST" and path == "/":
        form = parse_qs(body.decode("utf-8"))
        discipline = form.get("discipline", [""])[0].strip()
        grade = form.get("grade", [""])[0].strip()
        if not discipline or not grade:
            conn.sendall(response("400 Bad Request", "Нужны поля discipline и grade".encode("utf-8")))
            return
        grades.setdefault(discipline, []).append(grade)   # группировка по дисциплине
        # 303 See Other: после POST браузер перейдёт на GET / (без повторной отправки формы)
        conn.sendall(response("303 See Other", extra=["Location: /"]))
    else:
        conn.sendall(response("404 Not Found", "Страница не найдена".encode("utf-8")))


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"Откройте http://{HOST}:{PORT}")
        while True:
            conn, _ = srv.accept()
            with conn:
                try:
                    handle(conn)
                except (ValueError, OSError) as e:
                    print("Ошибка запроса:", e)


if __name__ == "__main__":
    main()
