import socket
import os
from urllib.parse import parse_qs

HOST = "localhost"
PORT = 8080

grades = {}

def create_page():
    grade_list = ""

    for subject, subject_grades in grades.items():
        grade_list += (
            f"<li><b>{subject}</b>: {', '.join(subject_grades)}</li>"
        )

    if not grade_list:
        grade_list = "<li>Оценок пока нет</li>"

    file_path = os.path.join(os.path.dirname(__file__), "index.html")

    with open(file_path, "r", encoding="utf-8") as file:
        html_template = file.read()

    return html_template.replace("{{GRADE_LIST}}", grade_list)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Сервер запущен на http://{HOST}:{PORT}")

while True:
    client_connection, client_address = server_socket.accept()

    request = b""

    while b"\r\n\r\n" not in request:
        request += client_connection.recv(1024)

    headers_data, body = request.split(b"\r\n\r\n", 1)
    headers_text = headers_data.decode("utf-8")

    lines = headers_text.split("\r\n")
    method, path, protocol = lines[0].split()

    headers = {}

    for line in lines[1:]:
        if ": " in line:
            name, value = line.split(": ", 1)
            headers[name.lower()] = value

    content_length = int(headers.get("content-length", 0))

    while len(body) < content_length:
        body += client_connection.recv(1024)

    if method == "POST":
        form_data = parse_qs(body.decode("utf-8"))

        subject = form_data.get("subject", [""])[0]
        grade = form_data.get("grade", [""])[0]

        if subject and grade:
            if subject not in grades:
                grades[subject] = []

            grades[subject].append(grade)

            print(f"Добавлена оценка: {subject} — {grade}")

    html_content = create_page()
    html_bytes = html_content.encode("utf-8")

    http_response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8")

    client_connection.sendall(http_response + html_bytes)
    client_connection.close()