import socket
from urllib.parse import parse_qs

grades = {}


def page():
    rows = "".join(
        f"<tr><td>{subject}</td><td>{', '.join(values)}</td></tr>"
        for subject, values in grades.items()
    )
    return f"""<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>Оценки</title></head>
<body>
<h1>Оценки по дисциплинам</h1>
<form method="post">
<input name="subject" placeholder="Дисциплина" required>
<input name="grade" type="number" min="1" max="5" required>
<button>Сохранить</button>
</form>
<table><tr><th>Дисциплина</th><th>Оценка</th></tr>{rows}</table>
</body>
</html>""".encode()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8085))
server.listen()
print("Grades server: http://127.0.0.1:8085")

while True:
    connection, _ = server.accept()
    request = connection.recv(8192).decode()
    if request.startswith("POST"):
        data = parse_qs(request.split("\r\n\r\n", 1)[1])
        subject = data["subject"][0]
        grades.setdefault(subject, []).append(data["grade"][0])
    body = page()
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        + f"Content-Length: {len(body)}\r\n\r\n".encode()
        + body
    )
    connection.sendall(response)
    connection.close()
