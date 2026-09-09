import socket
from dataclasses import dataclass
from email.parser import Parser
from urllib.parse import parse_qs, urlparse


HOST = 'localhost'
PORT = 8080
NAME = 'MyServer'

MAX_LINE = 64 * 1024
MAX_HEADERS = 100


@dataclass
class Request:
    method: str
    target: str
    version: str
    headers: dict
    body: str

    @property
    def url(self):
        return urlparse(self.target)

    @property
    def path(self):
        return self.url.path

    @property
    def query(self):
        return parse_qs(self.url.query)


class MyHTTPServer:
    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name

        # Предмет -> список оценок
        self.grades = {}

    def serve_forever(self):
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        serv_sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            print(
                f"[СЕРВЕР] Запущен на "
                f"http://{self._host}:{self._port}"
            )

            while True:
                conn, addr = serv_sock.accept()

                print(
                    f"[СЕРВЕР] Подключение от {addr}"
                )

                try:
                    self.serve_client(conn)

                except Exception as e:
                    print(
                        f"Client serving failed: {e}"
                    )

        except KeyboardInterrupt:
            print(
                "\n[СЕРВЕР] Остановка сервера..."
            )

        finally:
            serv_sock.close()

    def serve_client(self, conn):
        try:
            req = self.parse_request(conn)

            # Редирект с / на /grades
            if req.path == '/' and req.method == 'GET':
                self.send_response(
                    conn,
                    b'',
                    '302 Found',
                    ['Location: /grades\r\n']
                )
            else:
                resp = self.handle_request(req)

                self.send_response(
                    conn,
                    resp
                )

        except ConnectionResetError:
            conn = None

        except Exception as e:
            self.send_error(
                conn,
                e
            )

        if conn:
            conn.close()

    def parse_request(self, conn):
        rfile = conn.makefile('rb')

        method, target, version = \
            self.parse_request_line(rfile)

        headers = self.parse_headers(rfile)

        body = ''

        if method == 'POST':
            content_length = int(
                headers.get(
                    'Content-Length',
                    0
                )
            )

            if content_length > 0:
                body = rfile.read(
                    content_length
                ).decode('utf-8')

        host = headers.get('Host')

        if not host:
            raise Exception("Bad request")

        if host not in (
            f"{self._host}:{self._port}",
            self._host
        ):
            raise Exception("Not found")

        return Request(
            method,
            target,
            version,
            headers,
            body
        )

    def parse_request_line(self, rfile):
        raw = rfile.readline(
            MAX_LINE + 1
        )

        if len(raw) > MAX_LINE:
            raise Exception(
                "Request line is too long"
            )

        req_line = str(
            raw,
            'iso-8859-1'
        ).rstrip('\r\n')

        words = req_line.split(' ')

        if len(words) != 3:
            raise Exception(
                "Request line is malformed"
            )

        method, target, version = words

        if method not in ['GET', 'POST']:
            raise Exception(
                "Unknown HTTP method"
            )

        if version != 'HTTP/1.1':
            raise Exception(
                "Unknown HTTP version"
            )

        return method, target, version

    def parse_headers(self, rfile):
        headers = []

        while True:
            line = rfile.readline(
                MAX_LINE + 1
            )

            if len(line) > MAX_LINE:
                raise Exception(
                    "Header line is too long"
                )

            if line in (
                b'\r\n',
                b'\n',
                b''
            ):
                break

            headers.append(line)

        if len(headers) > MAX_HEADERS:
            raise Exception(
                'Too many headers'
            )

        sheaders = b''.join(
            headers
        ).decode('iso-8859-1')

        return Parser().parsestr(
            sheaders
        )

    def handle_request(self, req):
        if req.path == '/grades' \
                and req.method == 'GET':

            return self.handle_get_grades(req)

        elif req.path == '/grades' \
                and req.method == 'POST':

            return self.handle_post_grades(req)

        elif req.path == '/grades/add' \
                and req.method == 'GET':

            return self.handle_get_form(req)

        else:
            raise Exception("Not found")

    def handle_get_grades(self, req):
        with open(
                '../../files/grades.html',
                'r',
                encoding='utf-8'
        ) as file:
            html = file.read()

        if self.grades:
            grades_html = ""

            for subject, grades in self.grades.items():
                grades_html += f"""
                <div class="subject-card">
                    <h2>{subject}</h2>

                    <div class="grades">
                """

                for grade in grades:
                    grades_html += f"""
                        <span class="grade">{grade}</span>
                    """

                grades_html += """
                    </div>
                </div>
                """

        else:
            grades_html = """
            <div class="empty">
                <div class="empty-icon">📚</div>
                <h2>Оценок пока нет</h2>
                <p>Добавьте первую оценку, чтобы она появилась здесь.</p>
            </div>
            """

        html = html.replace(
            '<!-- GRADES -->',
            grades_html
        )

        return html.encode('utf-8')

    def handle_post_grades(self, req):
        data = parse_qs(req.body)

        subject = data.get(
            'subject',
            ['']
        )[0]

        grade = data.get(
            'grade',
            ['']
        )[0]

        if not subject or not grade:
            raise Exception(
                "Bad request: missing fields"
            )

        if subject not in self.grades:
            self.grades[subject] = []

        self.grades[subject].append(
            grade
        )

        print(
            f"[ОЦЕНКА] {subject}: {grade}"
        )

        with open(
            '../../files/success.html',
            'r',
            encoding='utf-8'
        ) as file:

            html = file.read()

        html = html.replace(
            'SUBJECT',
            subject
        )

        html = html.replace(
            'GRADE',
            grade
        )

        return html.encode('utf-8')

    def handle_get_form(self, req):
        with open(
            '../../files/add_grade.html',
            'r',
            encoding='utf-8'
        ) as file:

            html = file.read()

        return html.encode('utf-8')

    def send_response(
            self,
            conn,
            resp,
            status='200 OK',
            extra_headers=None):

        wfile = conn.makefile('wb')

        status_line = (
            f"HTTP/1.1 {status}\r\n"
        )

        wfile.write(
            status_line.encode(
                'iso-8859-1'
            )
        )

        headers = [
            f'Server: {self._server_name}\r\n',
            'Content-Type: text/html; charset=utf-8\r\n',
            f'Content-Length: {len(resp)}\r\n',
            'Connection: close\r\n'
        ]

        if extra_headers:
            headers.extend(extra_headers)

        headers.append('\r\n')

        for header in headers:
            wfile.write(
                header.encode(
                    'iso-8859-1'
                )
            )

        wfile.write(resp)
        wfile.flush()

    def send_error(self, conn, err):
        try:
            wfile = conn.makefile('wb')

            status = '404 Not Found'

            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Ошибка</title>

                <style>
                    body {{
                        font-family: Arial;
                        text-align: center;
                        padding: 50px;
                    }}

                    h1 {{
                        color: #d32f2f;
                    }}

                    p {{
                        color: #666;
                    }}

                    a {{
                        color: #2196F3;
                        text-decoration: none;
                    }}
                </style>
            </head>

            <body>

                <h1>Ошибка</h1>

                <p>{err}</p>

                <a href="/grades/add">
                    ← Вернуться к добавлению оценки
                </a>

            </body>
            </html>
            """.encode('utf-8')

            status_line = (
                f'HTTP/1.1 {status}\r\n'
            )

            wfile.write(
                status_line.encode(
                    'iso-8859-1'
                )
            )

            headers = [
                f'Server: {self._server_name}\r\n',
                'Content-Type: text/html; charset=utf-8\r\n',
                f'Content-Length: {len(body)}\r\n',
                'Connection: close\r\n',
                '\r\n'
            ]

            for header in headers:
                wfile.write(
                    header.encode(
                        'iso-8859-1'
                    )
                )

            wfile.write(body)
            wfile.flush()

        except Exception as e:
            print(
                f'Failed to send error: {e}'
            )


if __name__ == '__main__':
    serv = MyHTTPServer(
        HOST,
        PORT,
        NAME
    )

    try:
        serv.serve_forever()

    except KeyboardInterrupt:
        pass