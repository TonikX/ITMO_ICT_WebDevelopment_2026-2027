import socket
import json
from pathlib import Path
from urllib.parse import parse_qs
from html import escape

file = Path(__file__).with_name('grades.json')
GRADES = {}
if file.exists():
    GRADES = json.loads(file.read_text(encoding='utf-8'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen(5)
print("Откройте http://127.0.0.1:8080")

while True:
    client, addr = server.accept()
    with client, client.makefile('rb') as request:
        # Первая строка запроса, например: GET / HTTP/1.1.
        first_line = request.readline().decode().split()
        if not first_line:
            continue
        method, path, version = first_line

        headers = {}
        while True:
            line = request.readline()
            if line in (b'\r\n', b''):
                break
            key, value = line.decode().split(':', 1)
            headers[key.lower()] = value.strip()

        if method == 'POST':
            length = int(headers['content-length'])
            data = parse_qs(request.read(length).decode())
            subject = data['subject'][0]
            grade = data['grade'][0]
            if subject not in GRADES:
                GRADES[subject] = []
            GRADES[subject].append(grade)
            file.write_text(json.dumps(GRADES, ensure_ascii=False, indent=4), encoding='utf-8')
            # Перенаправление: обновление страницы не отправит оценку ещё раз.
            client.sendall(b'HTTP/1.1 303 See Other\r\nLocation: /\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            continue

        rows = ''
        for subject, marks in GRADES.items():
            rows += f'<tr><td>{escape(subject)}</td><td>{escape(", ".join(map(str, marks)))}</td></tr>'

        html = f'''<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Оценки</title></head>
<body>
    <h1>Журнал оценок</h1>
    <form method="post" action="/">
        Дисциплина: <input name="subject" required>
        Оценка: <input name="grade" type="number" min="2" max="5" required>
        <button>Добавить</button>
    </form>
    <table border="1">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
</body>
</html>'''.encode()
        response = (
            'HTTP/1.1 200 OK\r\n'
            'Content-Type: text/html; charset=utf-8\r\n'
            f'Content-Length: {len(html)}\r\n'
            'Connection: close\r\n\r\n'
        )
        client.sendall(response.encode() + html)


