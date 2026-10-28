import os
import socket
import threading
from urllib.parse import parse_qs
from html import escape

HOST = '127.0.0.1'
PORT = 9094
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'index.html')

FORM_HTML = """
<section class="form-card">
    <h2>Добавить оценку</h2>
    <form method="POST" action="/">
        <label>Дисциплина
            <input name="subject" required maxlength="60"
                   placeholder="Например, Математика">
        </label>
        <label>Оценка
            <input name="grade" type="number" min="1" max="5" required>
        </label>
        <button type="submit">Сохранить</button>
    </form>
</section>
"""

class GradesServer:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        # название_дисциплины: [список оценок]
        self.grades: dict[str, list[int]] = {}
        self.lock = threading.Lock()

        with open(TEMPLATE_PATH, encoding='utf-8') as f:
            self.template = f.read()

    def start(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"[Сервер] Сервер доступен по ссылке http://{self.host}:{self.port}")

        try:
            while True:
                conn, addr = server_socket.accept()
                threading.Thread(
                    target=self.handle_connection,
                    args=(conn, addr),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            print("\n[Сервер] Остановлен")
        finally:
            server_socket.close()

    def _route(self, method: str, path: str, body: str) -> bytes:
        path = path.split('?', 1)[0]  # отбрасываем query string

        if method == 'GET' and path == '/':
            return self._html_response(self._render_page(with_form=True))
        if method == 'GET' and path == '/grades':
            return self._html_response(self._render_page(with_form=False))
        if method == 'POST' and path == '/':
            self._handle_post(body)
            return self._html_response(self._render_page(with_form=True))

        return self._html_response(
            "<h1>404 Not Found</h1><a href='/'>На главную</a>",
            status='404 Not Found',
        )

    def handle_connection(self, conn: socket.socket, addr: tuple) -> None:
        try:
            request = self._read_request(conn)
            if request is None:
                return
            method, path, body = request
            print(f"[Сервер] {addr[0]} → {method} {path}")

            response = self._route(method, path, body)
            conn.sendall(response)
        except Exception as e:
            print(f"[Сервер] Ошибка при обработке {addr}: {e}")
        finally:
            conn.close()

    def _read_request(self, conn: socket.socket):
        """
        Читает запрос целиком: заголовки + тело
        Возвращает (method, path, body) или None при пустом запросе
        """
        raw = b''
        while b'\r\n\r\n' not in raw:
            chunk = conn.recv(4096)
            if not chunk:
                return None
            raw += chunk

        header_part, body_part = raw.split(b'\r\n\r\n', 1)
        headers_text = header_part.decode('utf-8', errors='ignore')
        lines = headers_text.split('\r\n')

        # Первая строка: "GET /path HTTP/1.1"
        method, path, *_ = lines[0].split()
        content_length = 0
        for line in lines[1:]:
            if line.lower().startswith('content-length:'):
                content_length = int(line.split(':', 1)[1].strip())
                break
        while len(body_part) < content_length:
            chunk = conn.recv(4096)
            if not chunk:
                break
            body_part += chunk

        body = body_part.decode('utf-8', errors='ignore')
        return method, path, body


    def _handle_post(self, body: str) -> None:
        """Парсит тело POST-запроса (form-urlencoded) и добавляет оценку"""
        params = parse_qs(body)  # {'subject': ['Математика'], 'grade': ['5']}
        subject = params.get('subject', [''])[0].strip()
        grade_raw = params.get('grade', [''])[0].strip()

        if not subject or not grade_raw:
            return

        try:
            grade = int(grade_raw)
        except ValueError:
            return

        if not 1 <= grade <= 5:
            return

        with self.lock:
            self.grades.setdefault(subject, []).append(grade)

        print(f"[Сервер] Добавлено: {subject} => {grade}")

    def _render_page(self, with_form: bool) -> str:
        """Подставляет в шаблон форму и строки журнала"""
        return (
            self.template
            .replace('{{FORM}}', FORM_HTML if with_form else '')
            .replace('{{ROWS}}', self._render_rows())
        )

    def _render_rows(self) -> str:
        with self.lock:
            snapshot = {subj: list(marks) for subj, marks in self.grades.items()}

        if not snapshot:
            return "<p class='empty'>Пока нет ни одной оценки</p>"

        parts = [
            "<table>",
            "<tr><th>Дисциплина</th><th>Оценки</th></tr>",
        ]
        for subject, marks in snapshot.items():
            badges = ''.join(f"<span class='badge'>{m}</span>" for m in marks)
            parts.append(
                f"<tr><td>{escape(subject)}</td><td>{badges}</td></tr>"
            )
        parts.append("</table>")
        return ''.join(parts)


    def _html_response(self, body: str, status: str = '200 OK') -> bytes:
        body_bytes = body.encode('utf-8')
        headers = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        return headers.encode('utf-8') + body_bytes

if __name__ == '__main__':
    GradesServer(HOST, PORT).start()


