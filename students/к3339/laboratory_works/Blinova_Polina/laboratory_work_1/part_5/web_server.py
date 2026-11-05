import socket
import os
import urllib.parse
from collections import defaultdict


class MyHTTPServer:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

        self.grades = defaultdict(list)

    def serve_forever(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print(f"Сервер '{self.name}' запущен на http://{self.host}:{self.port}")

        try:
            while True:
                client_socket, address = server_socket.accept()
                print(f"\nПодключен клиент: {address}")
                self.serve_client(client_socket)
        except KeyboardInterrupt:
            print("\nСервер остановлен")
        finally:
            server_socket.close()

    def serve_client(self, client_socket):
        try:
            request_file = client_socket.makefile('rb')

            method, url, params, protocol = self.parse_request(request_file)
            headers = self.parse_headers(request_file)

            result = self.handle_request(
                method, url, params, headers, request_file
            )

            if len(result) == 4:
                status, reason, body, content_type = result
                self.send_response(client_socket, status, reason, body, content_type)
            else:
                status, reason, body = result
                self.send_response(client_socket, status, reason, body)

        except Exception as e:
            print(f"Ошибка при обработке клиента: {e}")
            try:
                error_body = f"<h1>500 Internal Server Error</h1><p>{e}</p>"
                self.send_response(
                    client_socket, 500, "Internal Server Error", error_body
                )
            except Exception:
                print(f"Ошибка при обработке клиента: {e}\n Не удалось вывести информацию")
        finally:
            client_socket.close()

    def parse_request(self, request_file):
        first_line = request_file.readline().decode('utf-8').strip()

        if not first_line:
            raise ValueError("Пустой запрос")

        print(f"Запрос: {first_line}")

        parts = first_line.split(' ')
        if len(parts) != 3:
            raise ValueError(f"Некорректная строка запроса: {first_line}")

        method, url, protocol = parts

        if '?' in url:
            path, query_string = url.split('?', 1)
            params = urllib.parse.parse_qs(query_string)
        else:
            path = url
            params = {}

        return method, path, params, protocol

    def parse_headers(self, request_file):
        headers = {}

        while True:
            line = request_file.readline().decode('utf-8').strip()

            if not line:
                break

            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key] = value

        return headers

    def handle_request(self, method, url, params, headers, request_file):
        if method == 'POST':
            content_length = int(headers.get('Content-Length', 0))
            body = request_file.read(content_length)
            if body:
                form_params = urllib.parse.parse_qs(body.decode('utf-8'))
                params.update(form_params)

        if method == 'GET' and url.startswith('/static/'):
            return self._serve_static(url)

        if method == 'GET' and url == '/favicon.ico':
            return (204, "No Content", b"", 'text/plain')

        if method == 'GET' and url == '/':
            return self._handle_root()
        
        elif method == 'GET' and url == '/grades':
            return self._handle_grades()
        
        elif method == 'POST' and url == '/add_grade':
            return self._handle_add_grade(params)
        
        else:
            return self._handle_404()

    def send_response(self, client_socket, status, reason, body, content_type='text/html'):
        if isinstance(body, str):
            body_bytes = body.encode('utf-8')
        else:
            body_bytes = body

        response = f"HTTP/1.1 {status} {reason}\r\n"
        response += f"Content-Type: {content_type}; charset=utf-8\r\n"
        response += f"Content-Length: {len(body_bytes)}\r\n"
        response += f"Connection: close\r\n"
        response += f"Server: {self.name}\r\n"
        response += "\r\n"

        client_socket.sendall(response.encode('utf-8'))
        client_socket.sendall(body_bytes)

        print(f"Отправлен ответ: {status} {reason}")

    def _load_template(self, filename):
        path = os.path.join('templates', filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"<h1>Шаблон {filename} не найден</h1>"

    def _serve_static(self, url):
        try:
            with open('static/style.css', 'rb') as f:
                content = f.read()
            return (200, "OK", content, 'text/css')
        except FileNotFoundError:
            return (404, "Not Found", b"CSS not found", 'text/plain')

    def _handle_root(self, message=None, msg_type=None):
        message_html = ""
        if message:
            css_class = "success" if msg_type == "success" else "error"
            message_html = f'<div class="message {css_class}">{message}</div>'

        template = self._load_template('index.html')
        html = template.replace('{{MESSAGE}}', message_html)
        return (200, "OK", html)

    def _handle_add_grade(self, params):
        discipline_list = params.get('discipline', [])
        grade_list = params.get('grade', [])

        discipline = discipline_list[0].strip() if discipline_list else ''
        grade_str = grade_list[0].strip() if grade_list else ''

        if not discipline or not grade_str:
            return self._handle_root("Ошибка: заполните все поля", "error")

        try:
            grade = int(grade_str)
        except ValueError:
            return self._handle_root(
                "Ошибка: оценка должна быть числом", "error"
            )

        if grade < 1 or grade > 5:
            return self._handle_root(
                "Ошибка: оценка должна быть от 1 до 5", "error"
            )

        self.grades[discipline].append(grade)

        return self._handle_root(
            f"Оценка {grade} по предмету '{discipline}' добавлена",
            "success"
        )

    def _handle_grades(self):
        template = self._load_template('grades.html')

        if not self.grades:
            html = template.replace('{{GRADES}}', '<p>Пока нет оценок</p>')
            html = html.replace('{{TOTAL}}', '')
            return (200, "OK", html)

        grades_html = ""
        total_grades = 0

        for discipline in sorted(self.grades.keys()):
            grades = self.grades[discipline]
            total_grades += len(grades)
            avg = sum(grades) / len(grades)

            grades_html += f'<div class="subject">'
            grades_html += f'<div class="subject-name">{discipline}</div>'

            for grade in grades:
                grades_html += f'<span class="grade">{grade}</span>'

            grades_html += (
                f'<div class="stats">'
                f'Средняя: {avg:.2f} | Всего: {len(grades)}'
                f'</div>'
            )
            grades_html += '</div>'

        total_html = (
            f"Всего предметов: {len(self.grades)} | "
            f"Всего оценок: {total_grades}"
        )

        html = template.replace('{{GRADES}}', grades_html)
        html = html.replace('{{TOTAL}}', total_html)
        return (200, "OK", html)


if __name__ == '__main__':
    host = 'localhost'
    port = 8081
    name = 'GradeBookServer'

    serv = MyHTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass