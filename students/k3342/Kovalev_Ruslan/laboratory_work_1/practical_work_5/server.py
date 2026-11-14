import socket
from urllib.parse import parse_qs

journal = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 9090))
server.listen(1)

while True:
    conn, addr = server.accept()
    request = conn.recv(1024).decode('utf-8')
    
    if not request:
        conn.close()
        continue

    headers, _, body = request.partition('\r\n\r\n')
    method = headers.split(' ')[0]

    if method == 'POST':
        data = parse_qs(body)
        subject = data.get('subject', [''])[0]
        grade = data.get('grade', [''])[0]
        
        if subject and grade:
            if subject not in journal:
                journal[subject] = []
            journal[subject].append(grade)

    html_grades = "".join(f"<li>{s}: {', '.join(g)}</li>" for s, g in journal.items())
    
    html_body = f"""<!DOCTYPE html>
    <html lang="ru">
    <head><meta charset="UTF-8"><title>Журнал оценок</title></head>
    <body>
        <h2>Добавить оценку</h2>
        <form method="POST">
            Дисциплина: <input type="text" name="subject" required>
            Оценка: <input type="text" name="grade" required>
            <button type="submit">Отправить</button>
        </form>
        <h2>Список оценок</h2>
        <ul>{html_grades}</ul>
    </body>
    </html>"""

    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{html_body}"
    conn.sendall(response.encode('utf-8'))
    conn.close()