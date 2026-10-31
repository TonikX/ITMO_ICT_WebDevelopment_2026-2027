import socket
from urllib.parse import unquote
"http://localhost:8800/"
grades = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.bind(("localhost", 8800))
server_socket.listen(5)
print("Сервер запущен на порту 8000...")


def add_grade(subject, grade):
    if subject not in grades:
        grades[subject] = []
    grades[subject].append(grade)

def create_html():
    html = "<html><body>"
    html += "<h1>Журнал оценок</h1>"
    html += """
        <form method="POST">
            <label>Предмет:</label>
            <input type="text" name="subject">

            <label>Оценка:</label>
            <input type="number" name="grade">

            <button type="submit">Добавить</button>
        </form>
    """

    for subject, subject_grades in grades.items():
        html += f"<h2>{subject}</h2>"
        html += f"<p>{', '.join(map(str, subject_grades))}</p>"

    html += "</body></html>"

    return html

while True:
    client_connection, client_address = server_socket.accept()
    print(f"Подключился клиент: {client_address}")

    request = client_connection.recv(4096).decode("utf-8")
    print("HTTP-запрос:")
    print(request)

    first_line = request.split("\r\n")[0]
    method, path, version = first_line.split()
    print(f"Метод: {method}")

    
    if method == "GET":
        html = create_html()

        http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                f"Content-Length: {len(html.encode('utf-8'))}\r\n"
                "Connection: close\r\n"
                "\r\n"
                + html
        )
        client_connection.sendall(http_response.encode())

    elif method == "POST":
        body = ""
        if "\r\n\r\n" in request:
            body = request.split("\r\n\r\n", 1)[1]
        data = body.split("&")
        subject = unquote(data[0].split("=")[1]).replace("+", " ")
        grade = data[1].split("=")[1]
        grade = int(grade)
        add_grade(subject, grade)
        html = create_html()
        response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                f"Content-Length: {len(html.encode('utf-8'))}\r\n"
                "Connection: close\r\n"
                "\r\n"
                + html
        )

        client_connection.sendall(response.encode())
    client_connection.close()