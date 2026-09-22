import socket
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8081

grades = {}

def create_html():
    grades_html = ''

    for discipline, discipline_grades in grades.items():
        grades_html += (
            f'<li>{discipline}: '
            f'{', '.join(map(str, discipline_grades))}</li>'
        )

    html = f"""
    <!DOCTYPE html>
    <html lang = ru>
    <head>
        <meta charset='UTF-8'>
        <title>Журнал оценок</title>
    </head>
    
    <body>
        <h1>Журнал оценок</h1>
        <form method='POST' action='/'>
            <label>Дисциплина:</label>
            <input type='text' name='discipline' required>

            <br><br>

            <label>Оценка:</label>
            <input type='number' name='grade' min='1' max='5' required>

            <br><br>

            <button type='submit'>Добавить оценку</button>
        </form>

        <h2>Все оценки</h2>

        <ul>
            {grades_html}
        </ul>

    </body>
    </html> 
    """
    return html

def send_response(connection, html):
    body = html.encode("utf-8")

    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    response = headers.encode("utf-8") + body

    connection.sendall(response)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Сервер запущен: http://{HOST}:{PORT}")

while True:
    connection, client_address = server_socket.accept()

    try:
        # Получаем первую часть HTTP-запроса
        request = connection.recv(4096)

        if not request:
            continue

        # Разделяем заголовки и тело запроса
        header_data, separator, body = request.partition(b"\r\n\r\n")

        headers_text = header_data.decode("utf-8")
        request_line = headers_text.split("\r\n")[0]

        method, path, version = request_line.split()

        print(f"{method} {path}")

        # Обрабатываем POST-запрос
        if method == "POST":

            # Находим Content-Length
            content_length = 0

            for line in headers_text.split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":", 1)[1].strip())
                    break

            # Если тело пришло не полностью, получаем оставшуюся часть
            while len(body) < content_length:
                body += connection.recv(
                    content_length - len(body)
                )

            body_text = body.decode("utf-8")
            form_data = parse_qs(body_text)
            discipline = form_data.get("discipline", [""])[0].strip()
            grade = form_data.get("grade", [""])[0].strip()

            if discipline and grade:
                if discipline not in grades:
                    grades[discipline] = []

                grades[discipline].append(grade)

                print(f"Добавлена оценка: {discipline} — {grade}")
                print("Журнал:", grades)

        # Создаём актуальную HTML-страницу
        html = create_html()

        # Отправляем страницу браузеру
        send_response(connection, html)

    finally:
        connection.close()