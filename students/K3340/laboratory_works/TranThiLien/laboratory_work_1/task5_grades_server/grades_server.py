import socket
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8081

grades = {}


def create_response(status, body):
    body = body.encode("utf-8")

    response = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + body

    return response


def html_page():
    rows = ""

    if not grades:
        rows = """
        <tr>
            <td colspan="2">Оценок пока нет</td>
        </tr>
        """
    else:
        for subject, subject_grades in grades.items():
            grades_text = ", ".join(
                str(grade) for grade in subject_grades
            )

            average = sum(subject_grades) / len(subject_grades)

            rows += f"""
            <tr>
                <td>{subject}</td>
                <td>{grades_text}</td>
                <td>{average:.2f}</td>
            </tr>
            """

    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}

        table {{
            border-collapse: collapse;
            width: 700px;
        }}

        th, td {{
            border: 1px solid black;
            padding: 10px;
        }}

        th {{
            background-color: #eeeeee;
        }}

        form {{
            margin-bottom: 30px;
        }}

        input {{
            margin: 5px;
            padding: 5px;
        }}
    </style>
</head>

<body>

<h1>Журнал оценок</h1>

<form method="POST" action="/grades">

    <label>
        Дисциплина:
        <input type="text" name="subject" required>
    </label>

    <br>

    <label>
        Оценка:
        <input
            type="number"
            name="grade"
            min="1"
            max="5"
            required
        >
    </label>

    <br>

    <button type="submit">
        Добавить оценку
    </button>

</form>

<h2>Все оценки</h2>

<table>
    <tr>
        <th>Дисциплина</th>
        <th>Оценки</th>
        <th>Средний балл</th>
    </tr>

    {rows}

</table>

</body>
</html>
"""


def handle_request(request):
    lines = request.split("\r\n")

    if not lines:
        return create_response(
            "400 Bad Request",
            "<h1>400 Bad Request</h1>"
        )

    request_line = lines[0]

    parts = request_line.split()

    if len(parts) < 3:
        return create_response(
            "400 Bad Request",
            "<h1>400 Bad Request</h1>"
        )

    method = parts[0]
    path = parts[1]

    print(f"Метод: {method}, путь: {path}")

    # GET
    if method == "GET":

        if path == "/" or path == "/grades":
            return create_response(
                "200 OK",
                html_page()
            )

        return create_response(
            "404 Not Found",
            "<h1>404 Not Found</h1>"
        )

    # POST
    if method == "POST":

        if path != "/grades":
            return create_response(
                "404 Not Found",
                "<h1>404 Not Found</h1>"
            )

        header_end = request.find("\r\n\r\n")

        if header_end == -1:
            return create_response(
                "400 Bad Request",
                "<h1>400 Bad Request</h1>"
            )

        body = request[header_end + 4:]

        form_data = parse_qs(body)

        subject_values = form_data.get("subject")
        grade_values = form_data.get("grade")

        if not subject_values or not grade_values:
            return create_response(
                "400 Bad Request",
                "<h1>Необходимо указать дисциплину и оценку.</h1>"
            )

        subject = subject_values[0].strip()

        try:
            grade = int(grade_values[0])
        except ValueError:
            return create_response(
                "400 Bad Request",
                "<h1>Оценка должна быть числом.</h1>"
            )

        if not subject:
            return create_response(
                "400 Bad Request",
                "<h1>Название дисциплины не может быть пустым.</h1>"
            )

        if grade < 1 or grade > 5:
            return create_response(
                "400 Bad Request",
                "<h1>Оценка должна быть от 1 до 5.</h1>"
            )

        if subject not in grades:
            grades[subject] = []

        grades[subject].append(grade)

        print(
            f"Добавлена оценка: "
            f"{subject} -> {grade}"
        )

        return create_response(
            "200 OK",
            html_page()
        )

    return create_response(
        "405 Method Not Allowed",
        "<h1>405 Method Not Allowed</h1>"
    )


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(
    f"Web server запущен: "
    f"http://{HOST}:{PORT}"
)

while True:
    connection, address = server_socket.accept()

    print(f"Подключение: {address}")

    try:
        request = connection.recv(8192).decode(
            "utf-8",
            errors="replace"
        )

        response = handle_request(request)

        connection.sendall(response)

    except Exception as error:
        print(f"Ошибка: {error}")

        response = create_response(
            "500 Internal Server Error",
            "<h1>500 Internal Server Error</h1>"
        )

        connection.sendall(response)

    finally:
        connection.close()