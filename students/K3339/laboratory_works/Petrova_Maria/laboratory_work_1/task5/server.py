import socket
from urllib.parse import urlparse, parse_qs


class MyHTTPServer:
    # Параметры сервера
    def __init__(self, host, port, server_name):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.grades = {}

    def serve_forever(self):
        # 1. Запуск сервера на сокете, обработка входящих соединений
        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen()

            print("Сервер запущен")

            while True:
                conn, address = server_socket.accept()
                conn.settimeout(3)

                try:
                    self.serve_client(conn)
                except Exception as e:
                    print("Ошибка:", e)

        finally:
            server_socket.close()

    def serve_client(self, conn):
        # 2. Обработка клиентского подключения
        request = None

        try:
            request = self.parse_request(conn)

            if request is None:
                return

            response = self.handle_request(request)
            self.send_response(conn, response)

        except socket.timeout:
            pass

        except Exception as e:
            print("Ошибка при обработке клиента:", e)

        finally:
            if request:
                request["rfile"].close()

            conn.close()

    def parse_request(self, conn):
        # 3. Функция для обработки заголовка http+запроса.
        # Python, сокет предоставляет возможность создать вокруг него некоторую обертку,
        # которая предоставляет file object интерфейс. Это дает возможность построчно
        # обработать запрос. Заголовок всегда - первая строка. Первую строку нужно
        # разбить на 3 элемента (метод + url + версия протокола). URL необходимо
        # разбить на адрес и параметры.

        rfile = conn.makefile("rb")

        request_line = rfile.readline().decode("iso-8859-1").strip()

        if not request_line:
            raise Exception("Пустой HTTP-запрос")

        method, target, version = request_line.split()

        url = urlparse(target)
        path = url.path
        params = parse_qs(url.query)

        headers = self.parse_headers(rfile)

        return {
            "method": method,
            "path": path,
            "params": params,
            "version": version,
            "headers": headers,
            "rfile": rfile
        }

    def parse_headers(self, rfile):
        # 4. Функция для обработки headers.
        # Необходимо прочитать все заголовки после первой строки
        # до появления пустой строки и сохранить их в массив.

        headers = {}

        while True:
            line = rfile.readline().decode("iso-8859-1")

            if line in ("\r\n", "\n", ""):
                break

            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

        return headers

    def handle_request(self, request):
        # 5. Функция для обработки url в соответствии с нужным методом.
        # В случае данной работы нужно будет создать набор условий,
        # который обрабатывает GET или POST запрос.
        # GET запрос должен возвращать данные.
        # POST запрос должен записывать данные на основе переданных параметров.

        method = request["method"]
        path = request["path"]

        if method == "GET" and path == "/grades":
            return self.handle_get()

        if method == "POST" and path == "/grades":
            return self.handle_post(request)

        return {
            "status": 404,
            "reason": "Not Found",
            "body": "Страница не найдена"
        }

    def handle_get(self):
        with open("index.html", "r", encoding="utf-8") as file:
            body = file.read()

        grades_html = ""

        if not self.grades:
            grades_html = "<p>Оценок пока нет</p>"
        else:
            grades_html = "<ul>"

            for subject, grades in self.grades.items():
                grades_html += (
                    f"<li><b>{subject}:</b> {', '.join(grades)}</li>"
                )

            grades_html += "</ul>"

        body = body.replace("{{grades}}", grades_html)

        return {
            "status": 200,
            "reason": "OK",
            "body": body
        }

    def handle_post(self, request):
        headers = request["headers"]
        rfile = request["rfile"]

        content_length = int(headers.get("Content-Length", 0))

        body = rfile.read(content_length).decode("utf-8")
        params = parse_qs(body)

        if "subject" not in params or "grade" not in params:
            return {
                "status": 400,
                "reason": "Bad Request",
                "body": "Не указана дисциплина или оценка"
            }

        subject = params["subject"][0]
        grade = params["grade"][0]

        if subject not in self.grades:
            self.grades[subject] = []

        self.grades[subject].append(grade)

        return self.handle_get()

    def send_response(self, conn, response):
        # 6. Функция для отправки ответа.
        # Необходимо записать в соединение status line вида
        # HTTP/1.1 <status_code> <reason>.
        # Затем построчно записать заголовки и пустую строку,
        # обозначающую конец секции заголовков.

        body = response["body"].encode("utf-8")

        status_line = (
            f'HTTP/1.1 {response["status"]} '
            f'{response["reason"]}\r\n'
        )

        headers = (
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        conn.sendall(
            status_line.encode("iso-8859-1")
            + headers.encode("iso-8859-1")
            + body
        )


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8086
    name = "localhost"

    serv = MyHTTPServer(host, port, name)

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass