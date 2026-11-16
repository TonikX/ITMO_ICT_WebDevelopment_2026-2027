import socket
from urllib.parse import parse_qs

marks_dict = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 9050))
server.listen(5)
print("Сервер поднят по адресу http://localhost:9050 и ждет запрос")

while True:
    client_socket, client_address = server.accept()
    
    try:
        raw_request = client_socket.recv(2048)
        if not raw_request:
            client_socket.close()
            continue

        client_request = raw_request.decode('utf-8')

        if '\r\n\r\n' in client_request:
            request_headers, request_body = client_request.split('\r\n\r\n', 1)
        else:
            request_headers = client_request
            request_body = ''

        request_headers_lines = request_headers.splitlines()
        if not request_headers_lines:
            client_socket.close()
            continue

        request_headers_line = request_headers_lines[0]
        parts = request_headers_line.split()

        if len(parts) < 2:
            client_socket.close()
            print("Пришел мусорный пакет")
            continue

        method = parts[0]
        path = parts[1]

        if method == 'POST':
            parsed_body = parse_qs(request_body) # библиотека для парсинга html запросов
            subjects = parsed_body.get('subject')
            marks = parsed_body.get('mark')

            if subjects and marks:
                subject = subjects[0].strip()
                mark = marks[0].strip()
                
                if subject not in marks_dict:
                    marks_dict[subject] = []
                marks_dict[subject].append(mark)
                print(f"Добавлена оценка {mark} по предмету {subject}")

                response_headers = (
                    "HTTP/1.1 303 See Other\r\n"
                    "Location: /\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )

                client_socket.sendall(response_headers.encode('utf-8'))

        else:
            marks_html = ""
            for sub, list_of_marks in marks_dict.items():
                str_marks = ", ".join(list_of_marks)
                marks_html += f"<li><b>{sub}</b>: {str_marks}</li>"
            if not marks_html:
                marks_html = "<li>В журнале нет оценок, сначала добавьте их</li>"

            try:
                with open('marks.html', 'r', encoding='utf-8') as f:
                    html_template = f.read()
            except FileNotFoundError:
                html_template = "<h1>Файл marks.html не найден на сервере</h1>"

            final_html = html_template.replace("%MARKS_LIST%", marks_html)
            response_final = final_html.encode('utf-8')

            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(response_final)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client_socket.sendall(response_headers.encode('utf-8') + response_final)
    except Exception as e:
        print(f"Ошибка при обработке запроса {e}")

    finally:
        client_socket.close()




