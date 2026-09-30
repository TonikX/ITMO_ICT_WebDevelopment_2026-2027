# базовый класс для написания http-сервера
import socket
from urllib.parse import parse_qs, urlparse
import sys


class MyHTTPServer:
    # Параметры сервера
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.grades = {}

    def serve_forever(self):
        # 1. Запуск сервера на сокете, обработка входящих соединений
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen()
        print(f"Сервер запущен на хост: {self.host} порт: {self.port} ")
        while True:
            conn, addr = sock.accept()
            self.serve_client(conn)
            conn.close()

    def serve_client(self, conn):

        # 2. Обработка клиентского подключения
        file = conn.makefile("r", encoding="utf-8")
        request = file.readline().strip()
        if not request:
            return
        print(request)
        method, path, params = self.parse_request(request)
        headers = self.parse_headers(file)
        print(method, path, '-------------------')
        body = ""
        if "content-length" in headers:
            body = file.read(int(headers["content-length"]))
        status, html = self.handle_request(method, body)
        self.send_response(conn, status, html)

    def parse_request(self, request_line):
        method, url, version = request_line.split()
        parsed = urlparse(url)
        path = parsed.path
        params = parse_qs(parsed.query)
        return method, path, params

        # 3. функция для обработки заголовка http+запроса. Python, сокет предоставляет возможность создать вокруг него некоторую обертку, которая предоставляет file object интерфейс. Это дайте возможность построчно обработать запрос. Заголовок всегда - первая строка. Первую строку нужно разбить на 3 элемента  (метод + url + версия протокола). URL необходимо разбить на адрес и параметры (isu.ifmo.ru/pls/apex/f?p=2143 , где isu.ifmo.ru/pls/apex/f, а p=2143 - параметр p со значением 2143)

    def parse_headers(self, file):
        headers = {}
        while True:
            line = file.readline().strip()
            if not line:
                break
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
        return headers

    # 4. Функция для обработки headers. Необходимо прочитать все заголовки после первой строки до появления пустой строки и сохранить их в массив.

    def handle_request(self, method, body):
        if method == "POST":
            data = parse_qs(body)
            subject = data.get("subject", [""])[0].strip()
            grade = data.get("grade", [""])[0].strip()
            if subject and grade.isdigit():
                self.grades.setdefault(subject, []).append(int(grade))
                print(self.grades)
        return 200, self.render_page()

    # 5. Функция для обработки url в соответствии с нужным методом. В случае данной работы, нужно будет создать набор условий, который обрабатывает GET или POST запрос. GET запрос должен возвращать данные. POST запрос должен записывать данные на основе переданных параметров.

    def send_response(self, conn, status, body):
        body_bytes = body.encode('utf-8')
        head = (f"HTTP/1.1 {status} OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                f"Content-Length: {len(body_bytes)}\r\n"
                "Connection: close\r\n"
                "\r\n")
        conn.sendall(head.encode("utf-8") + body_bytes)

    def render_page(self):
        grades_html = ""
        for subject, marks in self.grades.items():
            grades_html += f"<p>{subject}: {', '.join(str(m) for m in marks)}</p>"
        return """<h1>Журнал оценок</h1>
               <form method="post" action="/">
                   <input type="text" name="subject" placeholder="Дисциплина">
                   <input type="text" name="grade" placeholder="Оценка">
                   <button type="submit">Сохранить</button>
               </form>
               """ + grades_html


# 6. Функция для отправки ответа. Необходимо записать в соединение status line вида HTTP/1.1 <status_code> <reason>. Затем, построчно записать заголовки и пустую строку, обозначающую конец секции заголовков.

if __name__ == '__main__':
    host = "localhost"
    port = 8080
    name = "-Gradebook-"
    serv = MyHTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
