from pathlib import Path
import socket
from urllib.parse import parse_qs

HOST = 'localhost'
PORT = 8080

grades = {}

TEMPLATE = Path(__file__).parent.joinpath('index.html').read_text(encoding='utf-8')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print("Сервер запущен по адресу: localhost:8080 и ожидает...")


def render_page():
    if not grades:
        items = "<li>Оценок нет</li>"
    else:
        items = "".join(
            f"<li>{subject}: {marks}</li>" for subject, marks in grades.items()
        )
    return TEMPLATE.replace("{{GRADES}}", items)


def parse_request(request):
    head, _, body = request.partition(b"\r\n\r\n")
    print(request)
    lines = head.decode('utf-8').split("\r\n")

    method, path, _ = lines[0].split()
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            k, v = line.split(':', 1)
            headers[k.strip().lower()] = v.strip()

    return method, path, headers, body


def make_response(status, body, content_type="text/html; charset=utf-8"):
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode('utf-8')
    return headers + body


while True:
    client_connection, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    try:
        request = client_connection.recv(1024)

        method, path, headers, body = parse_request(request)

        print(f"{method} {path}")

        if method == "GET" and path == "/":
            response = make_response("200 OK", render_page().encode('utf-8'))

        elif method == "POST" and path == "/":
            params = parse_qs(body.decode('utf-8'))
            subject = params.get('subject', [''])[0].strip()
            grade = params.get('grade', [''])[0].strip()

            if subject and grade.isdigit():
                if subject not in grades:
                    grades[subject] = []
                grades[subject].append(int(grade))
                print(f"Сохранено: {subject} = {grade}")

            redirect_headers = (
                "HTTP/1.1 303 See Other\r\n"
                "Location: /\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode('utf-8')
            response = redirect_headers

        else:
            response = make_response(
                "404 Not Found",
                b"<h1>404 Not Found</h1>",
            )

        client_connection.sendall(response)

    except Exception as e:
        print(f"Ошибка обработки запроса: {e}")
    finally:
        client_connection.close()