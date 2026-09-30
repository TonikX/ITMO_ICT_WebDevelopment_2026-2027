import socket
from urllib.parse import parse_qs


grades = {}


def create_page_with_grades():
    grades_html = ""

    for subject, subject_grades in grades.items():
        grades_html += f"<h3>{subject}</h3>"
        grades_html += f"<p>Оценки: {', '.join(subject_grades)}</p>"

    if not grades_html:
        grades_html = "<p>Оценок пока нет.</p>"

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Журнал оценок</title>
    </head>
    <body>
        <h1>Журнал оценок</h1>
        {grades_html}
    </body>
    </html>
    """


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8084))
server_socket.listen()
print("Сервер запущен на http://localhost:8084")

while True:
    client_socket, client_address = server_socket.accept()
    request = client_socket.recv(1024).decode("utf-8")

    if not request:
        client_socket.close()
        continue

    # Получаем метод и путь из первой строки запроса
    request_line = request.split("\r\n")[0]
    method, path, _ = request_line.split()

    print(method, path)

    # Если пришел POST, сохраняем оценку
    if method == "POST" and path == "/add":
        body = request.split("\r\n\r\n", 1)[1]
        form_data = parse_qs(body)
        subject = form_data["subject"][0]
        grade = form_data["grade"][0]

        grades.setdefault(subject, []).append(grade)

    # После GET и POST показываем страницу
    html = create_page_with_grades()
    html_bytes = html.encode("utf-8")

    response_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    client_socket.sendall(response_headers.encode("utf-8") + html_bytes)
    client_socket.close()
