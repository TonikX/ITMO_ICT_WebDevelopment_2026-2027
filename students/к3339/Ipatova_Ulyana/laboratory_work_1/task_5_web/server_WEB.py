import socket
from urllib.parse import parse_qs

grades = {}

def receive_request(client_socket):
    request = b""
    while b"\r\n\r\n" not in request:
        data = client_socket.recv(1024)
        if not data:
            return None
        request += data

    headers_part, body = request.split(b"\r\n\r\n", 1)
    headers_text = headers_part.decode()
    content_length = 0
    for line in headers_text.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
    while len(body) < content_length:
        data = client_socket.recv(1024)
        if not data:
            break
        body += data
    return headers_part + b"\r\n\r\n" + body

def parse_request(request):
    headers_part, body = request.split(b"\r\n\r\n", 1)
    headers_text = headers_part.decode()
    lines = headers_text.split("\r\n")
    request_line = lines[0]
    method, path, version = request_line.split()
    headers = {}
    for line in lines[1:]:
        key, value = line.split(":", 1)
        headers[key] = value.strip()
    body = body.decode()
    return method, path, headers, body

def add_grade(body):
    try: 
        form_data = parse_qs(body)

        subject = form_data["subject"][0].strip()
        grade = int(form_data["grade"][0])
        if subject == "":
            return "Название дисциплины не может быть пустым"
        if subject.isdigit():
            return "Название дисциплины должно содержать текст"
        if grade < 2 or grade > 5:
            return "Оценка должна быть от 2 до 5"
    
        if subject not in grades:
            grades[subject] = []

        grades[subject].append(grade)

        print("Текущие оценки:", grades)
        return None
    except (KeyError, ValueError):
        return "Некорректные данные"

def generate_html():
    html = """<html><body><h1>Журнал оценок</h1>"""

    for subject, subject_grades in grades.items():
        html += f"<h2>{subject}</h2>"
        html += f"<p>{subject_grades}</p>"

    html += """
    <h2>Добавить оценку</h2>
    <form action="/grade" method="POST">
        <label>Дисциплина:</label>
        <input type="text" name="subject" required pattern=".*[A-Za-zА-Яа-яЁё].*" title="Название дисциплины должно содержать буквы"><br>
        <label>Оценка:</label>
        <input type="number" name="grade" min="2" max="5" required><br>
        <button type="submit">Добавить</button>
    </form>
    </body>
    </html>
    """

    return html

def send_response(client_socket, html):
    body = html.encode()
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    client_socket.sendall(headers.encode() + html.encode())
    



def handle_client(client_socket):
    request = receive_request(client_socket)
    if request is None:
        return

    method, path, headers, body = parse_request(request)

    print("Метод:", method)
    print("Путь:", path)

    if method == "POST" and path == "/grade":
        add_grade(body)
        html = generate_html()
        send_response(client_socket, html)
    elif method == "GET" and path == "/":
        html = generate_html()
        send_response(client_socket, html)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))
server_socket.listen(5)
print("HTTP сервер запущен...")

while True:
    client_connection, client_address = server_socket.accept()
    print(f'Подключение от {client_address}')
    handle_client(client_connection) 
    client_connection.close()
    

