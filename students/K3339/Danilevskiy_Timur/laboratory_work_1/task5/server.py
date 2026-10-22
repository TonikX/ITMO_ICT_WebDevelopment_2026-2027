"""Задание 5. Веб-сервер на сокетах для учёта оценок по дисциплинам.

GET  /  — HTML-страница с формой и таблицей всех оценок
POST /  — добавить оценку (тело формы: discipline=...&grade=...)

Оценки хранятся в словаре {дисциплина: [оценки]}, поэтому у каждой
дисциплины ровно одна запись со списком всех её оценок.
"""
import socket
from html import escape
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8081
MAX_LINE = 64 * 1024
MAX_HEADERS = 100
MIN_GRADE, MAX_GRADE = 2, 5


class HTTPError(Exception):
    def __init__(self, status, reason, message=""):
        super().__init__(message or reason)
        self.status = status
        self.reason = reason
        self.message = message or reason


class Request:
    def __init__(self, method, target, version, headers, rfile):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.rfile = rfile

    @property
    def path(self):
        return self.target.split("?", 1)[0]

    def body(self):
        """Читает тело запроса: ровно Content-Length байт после заголовков."""
        length = self.headers.get("content-length")
        if not length:
            return b""
        try:
            return self.rfile.read(int(length))
        except ValueError:
            raise HTTPError(400, "Bad Request", "Некорректный Content-Length")


class Response:
    def __init__(self, status, reason, headers=None, body=b""):
        self.status = status
        self.reason = reason
        self.headers = headers or {}
        self.body = body


class MyHTTPServer:
    def __init__(self, host, port, server_name):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.grades = {}  # дисциплина -> список оценок

    def serve_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            print(f"Сервер {self.server_name} запущен: http://{self.host}:{self.port}/")

            while True:
                conn, _ = server.accept()
                try:
                    self.serve_client(conn)
                except Exception as e:
                    print(f"Ошибка обработки клиента: {e}")

    def serve_client(self, conn):
        with conn:
            request = None
            try:
                request = self.parse_request(conn)
                if request is None:
                    return
                response = self.handle_request(request)
            except HTTPError as e:
                response = self.error_response(e)

            request_line = f"{request.method} {request.target}" if request else "<некорректный запрос>"
            print(f"{request_line} -> {response.status} {response.reason}")
            self.send_response(conn, response)

    def parse_request(self, conn):
        rfile = conn.makefile("rb")

        # Стартовая строка: "МЕТОД ПУТЬ ВЕРСИЯ"
        raw = rfile.readline(MAX_LINE + 1)
        if not raw:
            return None  # клиент закрыл соединение, ничего не отправив
        if len(raw) > MAX_LINE:
            raise HTTPError(400, "Bad Request", "Слишком длинная строка запроса")

        parts = raw.decode("iso-8859-1").rstrip("\r\n").split()
        if len(parts) != 3:
            raise HTTPError(400, "Bad Request", "Некорректная строка запроса")
        method, target, version = parts
        if version not in ("HTTP/1.0", "HTTP/1.1"):
            raise HTTPError(505, "HTTP Version Not Supported")

        headers = self.parse_headers(rfile)
        return Request(method, target, version, headers, rfile)

    def parse_headers(self, rfile):
        # Заголовки идут построчно до пустой строки
        headers = {}
        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise HTTPError(400, "Bad Request", "Слишком длинный заголовок")
            if line in (b"\r\n", b"\n", b""):
                break
            name, sep, value = line.decode("iso-8859-1").partition(":")
            if not sep:
                raise HTTPError(400, "Bad Request", "Некорректный заголовок")
            # имена заголовков нечувствительны к регистру
            headers[name.strip().lower()] = value.strip()
            if len(headers) > MAX_HEADERS:
                raise HTTPError(400, "Bad Request", "Слишком много заголовков")
        return headers

    def handle_request(self, request):
        if request.path != "/":
            raise HTTPError(404, "Not Found", "Страница не найдена")
        if request.method == "GET":
            return self.handle_get_grades()
        if request.method == "POST":
            return self.handle_post_grade(request)
        raise HTTPError(405, "Method Not Allowed", "Метод не поддерживается")

    def handle_get_grades(self):
        return self.html_response(200, "OK", self.render_page())

    def handle_post_grade(self, request):
        fields = parse_qs(request.body().decode("utf-8"))
        discipline = " ".join(fields.get("discipline", [""])[0].split())
        grade = fields.get("grade", [""])[0].strip()

        if not discipline:
            raise HTTPError(400, "Bad Request", "Укажите название дисциплины")
        if not grade.isdigit() or not MIN_GRADE <= int(grade) <= MAX_GRADE:
            raise HTTPError(400, "Bad Request", f"Оценка должна быть целым числом от {MIN_GRADE} до {MAX_GRADE}")

        self.grades.setdefault(discipline, []).append(int(grade))

        # Post/Redirect/Get: после POST отправляем браузер обратно на GET /,
        # чтобы обновление страницы не отправляло форму повторно
        return Response(303, "See Other", {"Location": "/"})

    def render_page(self):
        if self.grades:
            rows = "\n".join(
                f"<tr><td>{escape(discipline)}</td>"
                f"<td>{', '.join(map(str, marks))}</td>"
                f"<td>{sum(marks) / len(marks):.2f}</td></tr>"
                for discipline, marks in self.grades.items()
            )
        else:
            rows = '<tr><td colspan="3" class="empty">Оценок пока нет</td></tr>'

        options = "\n".join(
            f'<option value="{grade}">{grade}</option>'
            for grade in range(MAX_GRADE, MIN_GRADE - 1, -1)
        )
        known = "\n".join(f'<option value="{escape(d)}">' for d in self.grades)

        return PAGE_TEMPLATE.format(rows=rows, options=options, known=known)

    def error_response(self, error):
        body = ERROR_TEMPLATE.format(status=error.status, reason=error.reason, message=escape(error.message))
        return self.html_response(error.status, error.reason, body)

    def html_response(self, status, reason, html):
        return Response(status, reason, {"Content-Type": "text/html; charset=utf-8"}, html.encode("utf-8"))

    def send_response(self, conn, response):
        headers = {
            **response.headers,
            "Content-Length": str(len(response.body)),
            "Connection": "close",
            "Server": self.server_name,
        }
        head = f"HTTP/1.1 {response.status} {response.reason}\r\n"
        head += "".join(f"{name}: {value}\r\n" for name, value in headers.items())
        head += "\r\n"
        conn.sendall(head.encode("utf-8") + response.body)


STYLE = """
<style>
    body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
           background: #f4f5f7; color: #1f2328; }
    main { max-width: 720px; margin: 48px auto; padding: 32px; background: #fff;
           border: 1px solid #d0d7de; border-radius: 8px; }
    h1 { margin-top: 0; font-size: 26px; }
    form { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px; }
    input, select, button { font: inherit; padding: 8px 10px; border: 1px solid #d0d7de;
                            border-radius: 6px; }
    input { flex: 1; min-width: 200px; }
    button { background: #1f6feb; color: #fff; border-color: #1f6feb; cursor: pointer; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 10px; border-bottom: 1px solid #d0d7de; }
    th { background: #f6f8fa; }
    .empty { color: #656d76; text-align: center; }
</style>
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Оценки по дисциплинам</title>
""" + STYLE.replace("{", "{{").replace("}", "}}") + """
</head>
<body>
<main>
    <h1>Оценки по дисциплинам</h1>
    <form method="POST" action="/">
        <input name="discipline" list="disciplines" placeholder="Дисциплина" required>
        <datalist id="disciplines">
{known}
        </datalist>
        <select name="grade">
{options}
        </select>
        <button type="submit">Добавить</button>
    </form>
    <table>
        <thead><tr><th>Дисциплина</th><th>Оценки</th><th>Средний балл</th></tr></thead>
        <tbody>
{rows}
        </tbody>
    </table>
</main>
</body>
</html>
"""

ERROR_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>{status} {reason}</title>
""" + STYLE.replace("{", "{{").replace("}", "}}") + """
</head>
<body>
<main>
    <h1>{status} {reason}</h1>
    <p>{message}</p>
    <p><a href="/">Вернуться к оценкам</a></p>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    try:
        MyHTTPServer(HOST, PORT, "grades-server").serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
