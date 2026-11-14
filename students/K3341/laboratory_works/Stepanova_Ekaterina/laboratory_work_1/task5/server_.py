import socket
from urllib.parse import parse_qs


SERVER_ADDR = ("localhost", 8080)
grades = {} #словарь для хранения всех оценок по предметам


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(SERVER_ADDR)
sock.listen()

while True:
    conn, addr = sock.accept()
    request = conn.recv(1024).decode()
    if not request:
        conn.close()
        continue
    print(request)

    # узнаем метод запроса
    first_line = request.split("\r\n")[0]
    method, path, version = first_line.split()
    print(method, '------------------')

    if method == "POST":
        body = request.split("\r\n\r\n")[1]
        print(body)
        params = parse_qs(body)
        subject = params["subject"][0]
        grade = params["grade"][0]
        grades.setdefault(subject, []).append(int(grade))
        print(grades)

    grades_html = ""
    for subject, grade in grades.items():
        grades_html += f"<p>{subject}: {', '.join(str(g) for g in grade)}</p>"
    # ответ
    html = """<h1>Журнал оценок</h1>
        <form method="post" action="/">
            <input type="text" name="subject" placeholder="Дисциплина">
            <input type="text" name="grade" placeholder="Оценка">
            <button type="submit">Сохранить</button>
        </form>
        """ + grades_html
    response = ("HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                "\r\n"
                + html)
    conn.sendall(response.encode())

    conn.close()
