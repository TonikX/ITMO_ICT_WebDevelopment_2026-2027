from collections import defaultdict
import select
import socket
import sys
from urllib.parse import parse_qs, urlparse


class MyHTTPServer:
    def __init__(self, host: str, port: int, server_name: str = "GradeBookServer"):
        self.host = host
        self.port = port
        self.server_name = server_name
        # Хранилище оценок: {'Математика': [5, 4], 'Физика': [5]}
        self.grades_db = defaultdict(list)

    def serve_forever(self):
        """Обрабатывает входящие соединения"""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(10)
        print(f"[{self.server_name}] Сервер запущен на http://{self.host}:{self.port}")

        try:
            while True:
                readable, _, _ = select.select([server_sock], [], [], 0.5)
                if server_sock in readable:
                    client_sock, client_addr = server_sock.accept()
                    try:
                        self.serve_client(client_sock)
                    except Exception as e:
                        print(f"Ошибка при обработке клиента {client_addr}: {e}")
                    finally:
                        client_sock.close()
        except KeyboardInterrupt:
            print("\n[OK] Сервер успешно остановлен (Ctrl+C).")
        finally:
            server_sock.close()

    def serve_client(self, client_sock: socket.socket):
        """Обрабатывает клиентское подключение"""
        rfile = client_sock.makefile("rb")

        # Чтение первой строки
        req_line = rfile.readline().decode("utf-8").strip()
        if not req_line:
            return

        method, path, query_params, version = self.parse_request(req_line)
        headers = self.parse_headers(rfile)

        # Чтение тела запроса при наличии Content-Length
        body = ""
        content_length = int(headers.get("Content-Length", 0))
        if content_length > 0:
            body_bytes = rfile.read(content_length)
            body = body_bytes.decode("utf-8")

        status_code, reason, resp_headers, resp_body = self.handle_request(
            method, path, query_params, headers, body
        )

        self.send_response(client_sock, status_code, reason, resp_headers, resp_body)

    def parse_request(self, req_line: str):
        """Разбирает первую строку HTTP-запроса"""
        words = req_line.split()
        if len(words) != 3:
            raise ValueError("Malformed request line")

        method, raw_url, version = words
        parsed_url = urlparse(raw_url)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        return method, path, query_params, version

    def parse_headers(self, rfile):
        """Парсит заголовок"""
        headers = {}
        while True:
            line = rfile.readline().decode("utf-8")
            if line in ("\r\n", "\n", ""):
                break
            if ":" in line:
                key, val = line.split(":", 1)
                headers[key.strip()] = val.strip()

        return headers

    def handle_request(self, method: str, path: str, query_params: dict, headers: dict, body: str):
        """Обрабатывает URL в соответствии с нужным методом (GET / POST)"""
        resp_headers = {"Content-Type": "text/html; charset=utf-8"}

        # Главная страница + страница просмотра журнала (GET)
        if method == "GET" and path in ("/", "/grades"):
            html_content = self._render_grades_page()
            return 200, "OK", resp_headers, html_content

        # Добавление новой оценки (POST)
        elif method == "POST" and path == "/add_grade":
            parsed_body = parse_qs(body)
            subject = parsed_body.get("subject", [None])[0]
            grade_str = parsed_body.get("grade", [None])[0]

            if subject and grade_str:
                subject = subject.strip()
                try:
                    grade = int(grade_str)
                    # Сохраняем оценку в список соответствующего предмета
                    self.grades_db[subject].append(grade)

                    # Возвращаем обновленную страницу
                    html_content = self._render_grades_page(
                        message=f"Успешно добавлена оценка {grade} по предмету '{subject}'!"
                    )
                    return 200, "OK", resp_headers, html_content
                except ValueError:
                    return 400, "Bad Request", resp_headers, "<h1>Ошибка: Оценка должна быть числом</h1>"

            return 400, "Bad Request", resp_headers, "<h1>Ошибка: Не переданы subject или grade</h1>"

        return 404, "Not Found", resp_headers, "<h1>404 Page Not Found</h1>"

    def _render_grades_page(self, message: str = "") -> str:
        """Вспомогательный метод для генерации HTML-страницы журнала"""
        rows = ""
        if not self.grades_db:
            rows = "<tr><td colspan='2'>Журнал пока пуст</td></tr>"
        else:
            for subject, grades in self.grades_db.items():
                grades_str = ", ".join(map(str, grades))
                rows += f"<tr><td><b>{subject}</b></td><td>{grades_str}</td></tr>\n"

        msg_html = f"<p style='color: green;'><b>{message}</b></p>" if message else ""

        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 500px; margin-top: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
        form {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; width: 470px; }}
        input {{ margin-bottom: 10px; padding: 5px; width: 95%; }}
        button {{ padding: 8px 15px; background: #28a745; color: white; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <h1>Электронный журнал оценок</h1>
    {msg_html}

    <form action="/add_grade" method="POST">
        <h3>Добавить оценку</h3>
        <label>Дисциплина:</label><br>
        <input type="text" name="subject" required placeholder="Например: Математика"><br>
        <label>Оценка:</label><br>
        <input type="number" name="grade" min="1" max="5" required placeholder="5"><br>
        <button type="submit">Сохранить</button>
    </form>

    <h2>Сводные оценки по предметам</h2>
    <table>
        <thead>
            <tr>
                <th>Дисциплина</th>
                <th>Оценки</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>"""

    def send_response(self, client_sock: socket.socket, status_code: int, reason: str, headers: dict, body: str):
        """6. Формирование status line, заголовков и отправка ответа"""
        body_bytes = body.encode("utf-8")

        headers["Content-Length"] = str(len(body_bytes))
        headers["Server"] = self.server_name
        headers["Connection"] = "close"

        response_lines = [f"HTTP/1.1 {status_code} {reason}"]
        for key, value in headers.items():
            response_lines.append(f"{key}: {value}")

        response_lines.append("")
        response_lines.append("")

        header_bytes = "\r\n".join(response_lines).encode("utf-8")
        client_sock.sendall(header_bytes + body_bytes)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 9003
    serv = MyHTTPServer(host, port)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        sys.exit(0)