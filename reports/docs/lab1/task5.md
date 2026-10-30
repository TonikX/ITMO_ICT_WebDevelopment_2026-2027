# Task 5 — Реализация HTTP-сервера для учёта оценок

## Цель задания
Разработать простой HTTP-сервер на Python с использованием сокетов, который позволяет:
- просматривать журнал оценок,
- добавлять новые оценки через HTML-форму.

## Реализация
```python
import socket
from collections import defaultdict
from urllib.parse import parse_qs

HOST = '127.0.0.1'
PORT = 8080

journal = defaultdict(list)

def generate_html():
    """Генерация HTML-страницы с формой ввода и сгруппированным журналом."""
    items_html = ""
    if not journal:
        items_html = "<p>Журнал пока пуст.</p>"
    else:
        items_html += "<table border='1' cellpadding='8' style='border-collapse: collapse;'>"
        items_html += "<tr><th>Дисциплина</th><th>Оценки</th></tr>"
        for subject, grades in journal.items():
            grades_str = ", ".join(grades)
            items_html += f"<tr><td><strong>{subject}</strong></td><td>{grades_str}</td></tr>"
        items_html += "</table>"

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Электронный журнал оценок</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; background-color: #f4f4f9; }}
        .container {{ max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        form {{ margin-bottom: 30px; }}
        input {{ width: 100%; padding: 8px; margin-top: 5px; margin-bottom: 15px; box-sizing: border-box; }}
        button {{ padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        button:hover {{ background-color: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Электронный журнал</h1>
        
        <form method="POST" action="/">
            <h3>Добавить запись</h3>
            <label>Название дисциплины:
                <input type="text" name="subject" placeholder="Например: Математика" required>
            </label>
            <label>Оценка:
                <input type="text" name="grade" placeholder="Например: 5" required>
            </label>
            <button type="submit">Сохранить оценку</button>
        </form>

        <h2>Сводная ведомость</h2>
        {items_html}
    </div>
</body>
</html>"""

def handle_request(client_socket):
    """Разбор HTTP-запроса и формирование ответа."""
    request_data = client_socket.recv(2048).decode('utf-8')
    if not request_data:
        client_socket.close()
        return

    lines = request_data.split('\r\n')
    request_line = lines[0]
    parts = request_line.split()

    if len(parts) < 2:
        client_socket.close()
        return

    method = parts[0]

    if method == 'GET':
        body = generate_html().encode('utf-8')
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
        ).encode('utf-8') + body
        client_socket.sendall(response)

    elif method == 'POST':
        body_start = request_data.find('\r\n\r\n')
        if body_start != -1:
            post_body = request_data[body_start + 4:]
            parsed_data = parse_qs(post_body)
            
            subject = parsed_data.get('subject', [''])[0].strip()
            grade = parsed_data.get('grade', [''])[0].strip()

            if subject and grade:
                journal[subject].append(grade)

        response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /\r\n"
            "Connection: close\r\n\r\n"
        ).encode('utf-8')
        client_socket.sendall(response)

    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Веб-сервер журнала запущен на http://{HOST}:{PORT}")

    while True:
        client_socket, _ = server.accept()
        handle_request(client_socket)

if __name__ == "__main__":
    main()
```