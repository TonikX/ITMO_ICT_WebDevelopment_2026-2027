import html
import socket
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8081
BUFFER_SIZE = 4096
ENCODING = "utf-8"


class GradeServer:
    def __init__(self) -> None:
        self._grades: dict[str, list[str]] = {}

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            server_socket.bind((HOST, PORT))
            server_socket.listen()

            print(f"Веб-сервер запущен на {HOST}:{PORT}")
            print(f"Откройте в браузере: http://{HOST}:{PORT}")
            print("Ожидание HTTP-запросов...")

            try:
                while True:
                    client_socket, client_address = server_socket.accept()

                    with client_socket:
                        request = self._receive_request(client_socket)

                        if not request:
                            continue

                        print(f"\nПодключён клиент: {client_address}")
                        self._handle_request(client_socket, request)

            except KeyboardInterrupt:
                print("\nСервер остановлен.")

    def _receive_request(self, client_socket: socket.socket) -> bytes:
        request = b""

        while b"\r\n\r\n" not in request:
            chunk = client_socket.recv(BUFFER_SIZE)

            if not chunk:
                return b""

            request += chunk

        headers, body = request.split(b"\r\n\r\n", 1)

        content_length = 0

        for line in headers.decode(ENCODING, errors="ignore").split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":", 1)[1].strip())

        while len(body) < content_length:
            chunk = client_socket.recv(BUFFER_SIZE)

            if not chunk:
                break

            body += chunk

        return headers + b"\r\n\r\n" + body

    def _handle_request(
        self,
        client_socket: socket.socket,
        request: bytes,
    ) -> None:
        headers, body = request.split(b"\r\n\r\n", 1)

        header_text = headers.decode(ENCODING, errors="ignore")
        request_line = header_text.split("\r\n")[0]

        method, path, _ = request_line.split(" ", 2)

        print(f"Получен запрос: {method} {path}")

        if path != "/":
            self._send_response(
                client_socket,
                "404 Not Found",
                self._build_error_page("Страница не найдена"),
            )
            return

        if method == "GET":
            self._send_response(
                client_socket,
                "200 OK",
                self._build_page(),
            )
            return

        if method == "POST":
            self._handle_post(client_socket, body)
            return

        self._send_response(
            client_socket,
            "405 Method Not Allowed",
            self._build_error_page("Метод не поддерживается"),
        )

    def _handle_post(
        self,
        client_socket: socket.socket,
        body: bytes,
    ) -> None:
        form_data = parse_qs(body.decode(ENCODING))

        subject = form_data.get("subject", [""])[0].strip()
        grade = form_data.get("grade", [""])[0].strip()

        if not subject or not grade:
            self._send_response(
                client_socket,
                "400 Bad Request",
                self._build_error_page(
                    "Необходимо указать дисциплину и оценку"
                ),
            )
            return

        if subject not in self._grades:
            self._grades[subject] = []

        self._grades[subject].append(grade)

        print(f"Добавлена оценка: {subject} — {grade}")

        self._send_redirect(client_socket)

    def _build_page(self) -> str:
        rows = ""

        if self._grades:
            for subject, grades in self._grades.items():
                safe_subject = html.escape(subject)
                safe_grades = ", ".join(
                    html.escape(grade)
                    for grade in grades
                )

                rows += (
                    "<tr>"
                    f"<td>{safe_subject}</td>"
                    f"<td>{safe_grades}</td>"
                    "</tr>"
                )
        else:
            rows = (
                "<tr>"
                "<td colspan=\"2\">Оценок пока нет</td>"
                "</tr>"
            )

        return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>

    <h2>Добавить оценку</h2>

    <form method="POST" action="/">
        <label>
            Дисциплина:
            <input
                type="text"
                name="subject"
                required
            >
        </label>

        <br><br>

        <label>
            Оценка:
            <input
                type="text"
                name="grade"
                required
            >
        </label>

        <br><br>

        <button type="submit">
            Добавить
        </button>
    </form>

    <h2>Все оценки</h2>

    <table border="1" cellpadding="8">
        <tr>
            <th>Дисциплина</th>
            <th>Оценки</th>
        </tr>
        {rows}
    </table>
</body>
</html>
"""

    def _build_error_page(self, message: str) -> str:
        safe_message = html.escape(message)

        return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Ошибка</title>
</head>
<body>
    <h1>Ошибка</h1>
    <p>{safe_message}</p>
    <a href="/">Вернуться на главную страницу</a>
</body>
</html>
"""

    def _send_response(
        self,
        client_socket: socket.socket,
        status: str,
        page: str,
    ) -> None:
        body = page.encode(ENCODING)

        headers = (
            f"HTTP/1.1 {status}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode(ENCODING)

        client_socket.sendall(headers + body)

    def _send_redirect(
        self,
        client_socket: socket.socket,
    ) -> None:
        response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        client_socket.sendall(response.encode(ENCODING))


if __name__ == "__main__":
    GradeServer().run()