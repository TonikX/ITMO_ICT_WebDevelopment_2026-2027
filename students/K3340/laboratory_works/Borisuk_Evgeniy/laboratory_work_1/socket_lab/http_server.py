"""Сокетный HTTP-сервер страницы и оценок для заданий №3 и №5."""

from __future__ import annotations

import argparse
import html
import socket
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
REQUEST_BUFFER_BYTES = 4096
MAX_REQUEST_BYTES = 65_536
INDEX_PATH = Path(__file__).resolve().parent.parent / "index.html"
ROWS_PLACEHOLDER = "{{grades_rows}}"


@dataclass
class GradeBook:
    """Хранилище дисциплин и оценок на время работы HTTP-сервера."""

    grades: list[tuple[str, str]] = field(default_factory=list)

    def add(self, subject: str, grade: str) -> None:
        """Проверить и сохранить дисциплину с оценкой."""
        normalized_subject = subject.strip()
        normalized_grade = grade.strip()
        if not normalized_subject or not normalized_grade:
            raise ValueError("Дисциплина и оценка не должны быть пустыми")
        self.grades.append((normalized_subject, normalized_grade))


def build_http_response(
    body: str,
    status: str = "200 OK",
    content_type: str = "text/html; charset=utf-8",
) -> bytes:
    """Сформировать HTTP/1.1-ответ с корректной длиной тела."""
    encoded_body = body.encode("utf-8")
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(encoded_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("ascii") + encoded_body


def receive_http_request(connection: socket.socket) -> bytes:
    """Прочитать заголовки и заявленное в Content-Length тело запроса."""
    request = bytearray()

    while b"\r\n\r\n" not in request:
        chunk = connection.recv(REQUEST_BUFFER_BYTES)
        if not chunk:
            break
        request.extend(chunk)
        if len(request) > MAX_REQUEST_BYTES:
            raise ValueError("HTTP-запрос слишком большой")

    if b"\r\n\r\n" not in request:
        return bytes(request)

    raw_headers, body = bytes(request).split(b"\r\n\r\n", 1)
    content_length = _extract_content_length(raw_headers)

    while len(body) < content_length:
        chunk = connection.recv(min(REQUEST_BUFFER_BYTES, content_length - len(body)))
        if not chunk:
            break
        body += chunk
        if len(raw_headers) + len(body) > MAX_REQUEST_BYTES:
            raise ValueError("HTTP-запрос слишком большой")

    return raw_headers + b"\r\n\r\n" + body


def _extract_content_length(raw_headers: bytes) -> int:
    """Получить длину тела из HTTP-заголовков."""
    for header in raw_headers.decode("iso-8859-1").split("\r\n")[1:]:
        name, separator, value = header.partition(":")
        if separator and name.strip().lower() == "content-length":
            return int(value.strip())
    return 0


def _parse_request(request: bytes) -> tuple[str, str, bytes]:
    """Извлечь метод, путь и тело из полного HTTP-запроса."""
    raw_headers, separator, body = request.partition(b"\r\n\r\n")
    if not separator:
        raise ValueError("Неполный HTTP-запрос")

    request_line = raw_headers.decode("iso-8859-1").split("\r\n", 1)[0]
    parts = request_line.split()
    if len(parts) != 3:
        raise ValueError("Некорректная стартовая строка HTTP")

    method, path, _ = parts
    return method, path, body


def render_grades_page(
    grade_book: GradeBook,
    template_path: Path = INDEX_PATH,
) -> str:
    """Загрузить ``index.html`` и вставить строки с сохранёнными оценками."""
    template = template_path.read_text(encoding="utf-8")
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(subject)}</td>"
        f"<td>{html.escape(grade)}</td>"
        "</tr>"
        for subject, grade in grade_book.grades
    )
    return template.replace(ROWS_PLACEHOLDER, rows)


def handle_http_request(
    request: bytes,
    grade_book: GradeBook,
    template_path: Path = INDEX_PATH,
) -> bytes:
    """Обработать GET или POST и вернуть страницу со всеми оценками."""
    try:
        method, path, body = _parse_request(request)
    except ValueError as error:
        return build_http_response(
            f"<h1>400 Bad Request</h1><p>{html.escape(str(error))}</p>",
            "400 Bad Request",
        )

    if path != "/":
        return build_http_response("<h1>404 Not Found</h1>", "404 Not Found")

    if method == "POST":
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        subject = form.get("subject", [""])[0]
        grade = form.get("grade", [""])[0]
        try:
            grade_book.add(subject, grade)
        except ValueError as error:
            return build_http_response(
                f"<h1>400 Bad Request</h1><p>{html.escape(str(error))}</p>",
                "400 Bad Request",
            )
    elif method != "GET":
        return build_http_response(
            "<h1>405 Method Not Allowed</h1>",
            "405 Method Not Allowed",
        )

    try:
        page = render_grades_page(grade_book, template_path)
    except OSError as error:
        return build_http_response(
            f"<h1>500 Internal Server Error</h1><p>{html.escape(str(error))}</p>",
            "500 Internal Server Error",
        )
    return build_http_response(page)


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Последовательно принимать HTTP-запросы и хранить оценки в памяти."""
    grade_book = GradeBook()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"HTTP-сервер запущен: http://{host}:{port}")

        while True:
            connection, _ = server.accept()
            with connection:
                try:
                    request = receive_http_request(connection)
                    response = handle_http_request(request, grade_book)
                    connection.sendall(response)
                except (OSError, ValueError):
                    # Ошибка относится только к текущему клиентскому соединению.
                    continue


def main() -> None:
    """Прочитать аргументы командной строки и запустить HTTP-сервер."""
    parser = argparse.ArgumentParser(description="HTTP-сервер оценок на сокетах")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nСервер остановлен.")


if __name__ == "__main__":
    main()
