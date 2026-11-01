"""Веб-сервер журнала оценок: GET показывает, POST сохраняет.

Хранилище ``dict[предмет, список оценок]`` группирует оценки по дисциплине.
"""

import socket
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 11005

grades: dict[str, list[str]] = {}


def row(subject: str, marks: list[str]) -> str:
    """Строит строку таблицы для одной дисциплины.

    Args:
        subject: Название дисциплины.
        marks: Список оценок по ней.

    Returns:
        HTML-строка таблицы.
    """
    return f"<tr><td>{subject}</td><td>{', '.join(marks)}</td></tr>"


def page() -> str:
    """Строит HTML-страницу журнала и формы.

    Args:
        None.

    Returns:
        HTML-страница строкой.
    """
    rows = "".join(row(s, g) for s, g in grades.items()) or \
        '<tr><td colspan="2">Оценок пока нет</td></tr>'
    return (
        "<!doctype html><html lang=ru><head><meta charset=utf-8>"
        "<title>Журнал</title></head><body><h1>Журнал оценок</h1>"
        "<table border=1><tr><th>Дисциплина</th><th>Оценки</th></tr>"
        f"{rows}</table>"
        "<h2>Добавить</h2>"
        "<form method=POST action=/>Дисциплина: <input name=subject><br>"
        "Оценка: <input name=grade><br><input type=submit value=Отправить>"
        "</form></body></html>"
    )


def response(body: str, status: str = "200 OK") -> bytes:
    """Упаковывает HTML в HTTP-ответ.

    Args:
        body: Тело страницы.
        status: Строка статуса.

    Returns:
        Байты HTTP-ответа.
    """
    raw = body.encode("utf-8")
    head = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(raw)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("utf-8")
    return head + raw


def read_request(conn: socket.socket) -> str:
    """Читает HTTP-запрос целиком с учётом Content-Length.

    Args:
        conn: Сокет клиента.

    Returns:
        Текст запроса.
    """
    data = conn.recv(65536)
    head, _, body = data.partition(b"\r\n\r\n")
    try:
        length = int(
            next(
                line.split(b":", 1)[1].strip()
                for line in head.split(b"\r\n")
                if line.lower().startswith(b"content-length:")
            )
        )
    except StopIteration:
        length = 0
    while len(body) < length:
        body += conn.recv(65536)
    return (head + b"\r\n\r\n" + body).decode("utf-8", errors="replace")


def handle(raw: str) -> bytes:
    """Обрабатывает один HTTP-запрос.

    Args:
        raw: Текст запроса.

    Returns:
        Байты HTTP-ответа.
    """
    if not raw:
        return response("<h1>400</h1>", "400 Bad Request")
    method = raw.split(" ", 1)[0]
    _, _, body = raw.partition("\r\n\r\n")
    if method == "POST":
        form = parse_qs(body)
        subject = form.get("subject", [""])[0].strip()
        grade = form.get("grade", [""])[0].strip()
        if subject and grade:
            grades.setdefault(subject, []).append(grade)
        return response(page())
    if method == "GET":
        return response(page())
    return response("<h1>405</h1>", "405 Method Not Allowed")


def main() -> None:
    """Запускает веб-сервер журнала.

    Args:
        None.

    Returns:
        None.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"Журнал: {HOST}:{PORT}")
        while True:
            conn, _ = sock.accept()
            with conn:
                conn.sendall(handle(read_request(conn)))


if __name__ == "__main__":
    main()
