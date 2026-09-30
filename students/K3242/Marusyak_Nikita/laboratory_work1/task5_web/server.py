import socket
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8081

grades = {}


def generate_html():

    rows = ""

    for subject, marks in grades.items():

        marks_string = ", ".join(
            map(str, marks)
        )

        rows += f"""
        <tr>
            <td>{subject}</td>
            <td>{marks_string}</td>
        </tr>
        """

    if not rows:

        rows = """
        <tr>
            <td colspan="2">Оценок пока нет</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="ru">

<head>

    <meta charset="UTF-8">

    <title>Журнал оценок</title>

</head>

<body>

    <h1>Журнал оценок</h1>

    <form method="POST" action="/grade">

        <label>Дисциплина:</label>

        <input
            type="text"
            name="subject"
            required
        >

        <br><br>

        <label>Оценка:</label>

        <input
            type="number"
            name="grade"
            min="1"
            max="5"
            required
        >

        <br><br>

        <button type="submit">
            Добавить
        </button>

    </form>

    <hr>

    <h2>Все оценки</h2>

    <table border="1">

        <tr>
            <th>Дисциплина</th>
            <th>Оценки</th>
        </tr>

        {rows}

    </table>

</body>

</html>
"""


def create_response(
    status,
    body,
    content_type="text/html; charset=utf-8"
):

    body_bytes = body.encode("utf-8")

    response = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8")

    return response + body_bytes


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

print("Сервер запущен:")
print(f"http://{HOST}:{PORT}")


while True:

    client_socket, client_address = server_socket.accept()

    request = b""

    while b"\r\n\r\n" not in request:

        chunk = client_socket.recv(1024)

        if not chunk:
            break

        request += chunk


    if not request:

        client_socket.close()
        continue


    headers, _, body = request.partition(b"\r\n\r\n")

    header_text = headers.decode("utf-8")

    header_lines = header_text.split("\r\n")

    request_line = header_lines[0]

    method, path, protocol = request_line.split(" ")

    content_length = 0


    for line in header_lines[1:]:

        if line.lower().startswith("content-length:"):

            content_length = int(
                line.split(":", 1)[1].strip()
            )


    while len(body) < content_length:

        body += client_socket.recv(
            content_length - len(body)
        )


    print(f"{method} {path}")


    if method == "POST" and path == "/grade":

        form_data = parse_qs(
            body.decode("utf-8")
        )

        subject = form_data.get(
            "subject",
            [""]
        )[0]

        grade_text = form_data.get(
            "grade",
            [""]
        )[0]


        try:

            grade = int(grade_text)

            if 1 <= grade <= 5 and subject:

                if subject not in grades:
                    grades[subject] = []

                grades[subject].append(grade)

                print(
                    f"Добавлена оценка: "
                    f"{subject} -> {grade}"
                )

        except ValueError:

            pass


        response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("utf-8")


    elif method == "GET" and path == "/":

        html = generate_html()

        response = create_response(
            "200 OK",
            html
        )


    else:

        response = create_response(
            "404 Not Found",
            "<h1>404 Not Found</h1>"
        )


    client_socket.sendall(response)

    client_socket.close()
