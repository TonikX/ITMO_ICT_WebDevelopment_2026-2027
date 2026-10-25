import socket
from mock import evaluations

# 127.0.0.1:8080
HOST = "127.0.0.1"
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"HTTP сервер запущен на {HOST}:{PORT}...")

while True:
    client_socket, client_address = server_socket.accept()
    request = client_socket.recv(1024).decode("utf-8")
    print(request)

    first_line = request.split("\r\n")[0]
    method, path, version = first_line.split()

    if method == "GET":
        eval_html = "<ul>"

        for subject, grades in evaluations.items():
            eval_html += f"<li>{subject}: {', '.join(map(str, grades))}</li>"

        eval_html += "</ul>"

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Журнал с оценками</title>
        </head>
        <body>
            <h2>Оценки:</h2>
            {eval_html}
            <h2>Добавить оценку</h2>

            <form method="POST" action="/" enctype="text/plain">
                <input type="text" name="subject" placeholder="Предмет">
                <input style="width: 100px;" type="number" name="grade" min="1" max="5" placeholder="Оценка">
                <button type="submit">Добавить</button>
            </form>
        </body>
        </html>
        """

        html_bytes = html.encode("utf-8")

        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html_bytes)}\r\n"
            "\r\n"
        )

        response = headers.encode("utf-8") + html_bytes

        client_socket.sendall(response)

    elif method == "POST":
        body = request.split("\r\n\r\n")[1]

        lines = body.strip().split("\r\n")

        subject = lines[0].split("=")[1]
        grade = int(lines[1].split("=")[1])

        if subject not in evaluations:
            evaluations[subject] = []

        evaluations[subject].append(grade)
        response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /\r\n"
            "Content-Length: 0\r\n"
            "\r\n"
        )

        client_socket.sendall(response.encode("utf-8"))

    client_socket.close()