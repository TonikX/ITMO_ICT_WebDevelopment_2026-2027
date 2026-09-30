"""Тесты GET/POST и HTML-файла сокетного HTTP-сервера."""

import socket
import unittest
from urllib.parse import urlencode

from socket_lab.http_server import (
    GradeBook,
    INDEX_PATH,
    build_http_response,
    handle_http_request,
    receive_http_request,
)


def make_request(method: str, body: str = "", path: str = "/") -> bytes:
    """Сформировать HTTP-запрос для теста обработчика."""
    encoded_body = body.encode("utf-8")
    headers = (
        f"{method} {path} HTTP/1.1\r\n"
        "Host: localhost\r\n"
        f"Content-Length: {len(encoded_body)}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "\r\n"
    )
    return headers.encode("ascii") + encoded_body


class HttpResponseTests(unittest.TestCase):
    """Проверки структуры ответа и обязательных HTTP-сценариев."""

    def test_response_has_valid_utf8_content_length(self):
        """Content-Length вычисляется по байтам, а не по символам."""
        response = build_http_response("Привет")
        headers, body = response.split(b"\r\n\r\n", 1)

        self.assertIn(b"HTTP/1.1 200 OK", headers)
        self.assertIn(b"Content-Length: 12", headers)
        self.assertEqual(body.decode("utf-8"), "Привет")

    def test_get_loads_index_html(self):
        """GET возвращает страницу, загруженную из отдельного index.html."""
        grade_book = GradeBook()
        response = handle_http_request(make_request("GET"), grade_book)
        _, body = response.split(b"\r\n\r\n", 1)

        self.assertTrue(INDEX_PATH.is_file())
        self.assertTrue(response.startswith(b"HTTP/1.1 200 OK\r\n"))
        self.assertIn("Оценки по дисциплинам", body.decode("utf-8"))
        self.assertNotIn("{{grades_rows}}", body.decode("utf-8"))

    def test_post_saves_grade_and_get_returns_it(self):
        """POST сохраняет данные, которые затем присутствуют в GET-ответе."""
        grade_book = GradeBook()
        form = urlencode({"subject": "Web-программирование", "grade": "5"})

        post_response = handle_http_request(
            make_request("POST", form),
            grade_book,
        )
        get_response = handle_http_request(make_request("GET"), grade_book)
        _, get_body = get_response.split(b"\r\n\r\n", 1)

        self.assertTrue(post_response.startswith(b"HTTP/1.1 200 OK\r\n"))
        self.assertEqual(grade_book.grades, [("Web-программирование", "5")])
        self.assertIn("Web-программирование", get_body.decode("utf-8"))
        self.assertIn("<td>5</td>", get_body.decode("utf-8"))

    def test_post_rejects_blank_fields(self):
        """POST с пустой дисциплиной получает ответ 400."""
        grade_book = GradeBook()
        form = urlencode({"subject": "", "grade": "5"})

        response = handle_http_request(make_request("POST", form), grade_book)

        self.assertTrue(response.startswith(b"HTTP/1.1 400 Bad Request\r\n"))
        self.assertEqual(grade_book.grades, [])

    def test_unsupported_method_returns_405(self):
        """Неподдерживаемый HTTP-метод получает статус 405."""
        response = handle_http_request(make_request("PUT"), GradeBook())

        self.assertTrue(
            response.startswith(b"HTTP/1.1 405 Method Not Allowed\r\n")
        )

    def test_request_reader_receives_complete_post_body(self):
        """Чтение сокета учитывает Content-Length тела POST-запроса."""
        sender, receiver = socket.socketpair()
        request = make_request("POST", "subject=Web&grade=5")

        with sender, receiver:
            sender.sendall(request)
            self.assertEqual(receive_http_request(receiver), request)


if __name__ == "__main__":
    unittest.main()
