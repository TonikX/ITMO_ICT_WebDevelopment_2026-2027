import socket
from urllib.parse import parse_qs

HOST = "localhost"
PORT = 8084

# словарь для хранения оценок по дисциплинам
grades = {}

# создаем сокет по протоколу TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# привязываем сокет к адресу и порту
server_socket.bind((HOST, PORT))

# начинаем слушать входящие подключения
server_socket.listen(5)

print(f"Веб-сервер запущен на http://{HOST}:{PORT}")


# формируем HTML-страницу
def create_html():
    grades_html = ""

    # добавляем дисциплины и оценки на страницу
    for subject, subject_grades in grades.items():
        grades_string = ", ".join(subject_grades)
        grades_html += f"<li><b>{subject}</b>: {grades_string}</li>"

    # если оценок еще нет
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


# получаем HTTP-запрос от клиента
def receive_request(client_connection):
    request = b""

    # получаем данные, пока не получим все HTTP-заголовки
    while b"\r\n\r\n" not in request:
        data = client_connection.recv(4096)

        if not data:
            break

        request += data

    # разделяем заголовки и тело запроса
    headers, _, body = request.partition(b"\r\n\r\n")

    # определяем длину тела запроса
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
    # принимаем подключение от клиента
    client_connection, client_address = server_socket.accept()

    # получаем HTTP-запрос
    headers, body = receive_request(client_connection)

    # получаем первую строку HTTP-запроса
    request_line = headers.split("\r\n")[0]

    # определяем HTTP-метод
    method = request_line.split()[0]

    print(f"Получен запрос: {request_line}")

    # обрабатываем POST-запрос
    if method == "POST":
        # разбираем данные формы
        form_data = parse_qs(body)

        subject = form_data.get("subject", [""])[0]
        grade = form_data.get("grade", [""])[0]

        # сохраняем полученную оценку
        if subject and grade:
            # если дисциплины еще нет, создаем для нее список
            if subject not in grades:
                grades[subject] = []

            # добавляем оценку к дисциплине
            grades[subject].append(grade)

            print(f"Добавлена оценка: {subject} — {grade}")

    # формируем HTML-страницу
    html_content = create_html()
    html_bytes = html_content.encode("utf-8")

    # формируем HTTP-ответ
    http_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    # отправляем HTTP-ответ клиенту
    client_connection.sendall(
        http_headers.encode() + html_bytes
    )

    # закрываем соединение с клиентом
    client_connection.close()