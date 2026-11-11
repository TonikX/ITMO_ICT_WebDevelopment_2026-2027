import socket
from urllib.parse import parse_qs

HOST = "localhost"
PORT = 8085

grades = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(5)

print(f"Веб-сервер запущен на http://{HOST}:{PORT}")


def create_html():
    grades_html = ""

    for subject, subject_grades in grades.items():
        grades_string = ", ".join(subject_grades)
        grades_html += f"<li><b>{subject}</b>: {grades_string}</li>"

    if not grades_html:
        grades_html = "<li>Оценок пока нет</li>"

    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>

    <form method="POST" action="/">
        <label>
            Дисциплина:
            <input type="text" name="subject" required>
        </label>

        <br><br>

        <label>
            Оценка:
            <input type="number" name="grade" min="1" max="5" required>
        </label>

        <br><br>

        <button type="submit">Добавить оценку</button>
    </form>

    <h2>Все оценки</h2>

    <ul>
        {grades_html}
    </ul>
</body>
</html>
"""


def receive_request(client_connection):
    request = b""

    while b"\r\n\r\n" not in request:
        data = client_connection.recv(4096)

        if not data:
            break

        request += data

    headers, _, body = request.partition(b"\r\n\r\n")

    content_length = 0

    for header in headers.decode("utf-8").split("\r\n"):
        if header.lower().startswith("content-length:"):
            content_length = int(header.split(":")[1].strip())

    # получаем оставшуюся часть тела запроса
    while len(body) < content_length:
        data = client_connection.recv(4096)

        if not data:
            break

        body += data

    return headers.decode("utf-8"), body.decode("utf-8")


while True:
    client_connection, client_address = server_socket.accept()

    headers, body = receive_request(client_connection)

    request_line = headers.split("\r\n")[0]

    method = request_line.split()[0]

    print(f"Получен запрос: {request_line}")

    if method == "POST":
        form_data = parse_qs(body)

        subject = form_data.get("subject", [""])[0]
        grade = form_data.get("grade", [""])[0]

        if subject and grade:
            if subject not in grades:
                grades[subject] = []

            grades[subject].append(grade)

            print(f"Добавлена оценка: {subject} — {grade}")

    html_content = create_html()
    html_bytes = html_content.encode("utf-8")

    http_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    client_connection.sendall(
        http_headers.encode() + html_bytes
    )

    client_connection.close()