import socket
import json
import os
from urllib.parse import parse_qs

GRADES_FILE = 'grades.json'

# Загружаем журнал из файла, если он существует
if os.path.exists(GRADES_FILE):
    with open(GRADES_FILE, 'r', encoding='utf-8') as f:
        grades_db = json.load(f)
else:
    grades_db = {}  # {"Предмет": [оценка1, оценка2, ...]}


def save_db():
    with open(GRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(grades_db, f, ensure_ascii=False, indent=2)


def generate_html():
    html = "<html><head><meta charset='utf-8'><title>Журнал</title></head><body>"
    html += "<h1>Журнал оценок</h1>"

    if not grades_db:
        html += "<p>Журнал пуст.</p>"
    else:
        for subject, marks in grades_db.items():
            html += f"<h3>{subject}</h3><ul>"
            for mark in marks:
                html += f"<li>{mark}</li>"
            html += "</ul>"

    html += """
    <hr>
    <h2>Добавить оценку</h2>
    <form action="/add" method="POST">
        Предмет: <input type="text" name="subject"><br><br>
        Оценка: <input type="text" name="mark"><br><br>
        <input type="submit" value="Добавить">
    </form>
    </body></html>
    """
    return html.encode('utf-8')


def handle_request(request_text):
    lines = request_text.split('\r\n')
    request_line = lines[0]
    words = request_line.split()
    method, path = words[0], words[1]

    print(f"\n=== Получен запрос ===")
    print(f"Метод: {method}, Путь: {path}")

    if method == 'GET' and path == '/':
        body = generate_html()
        headers = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
        return headers.encode('utf-8') + body

    elif method == 'POST' and path == '/add':
        print(f"Полный запрос:\n{request_text}")

        # Ищем тело запроса
        body_start = request_text.find('\r\n\r\n')
        if body_start != -1:
            body_str = request_text[body_start + 4:]
        else:
            body_str = ''

        print(f"Тело запроса: '{body_str}'")

        # Парсим данные формы
        params = parse_qs(body_str)
        print(f"Распарсенные данные: {params}")

        subject = params.get('subject', [''])[0]
        mark = params.get('mark', [''])[0]

        print(f"Извлечено: предмет='{subject}', оценка='{mark}'")

        if subject and mark:
            if subject not in grades_db:
                grades_db[subject] = []
            grades_db[subject].append(mark)
            save_db()
            print(f"✓ Сохранено в grades.json")

        body = generate_html()
        headers = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
        return headers.encode('utf-8') + body

    return b"HTTP/1.1 404 Not Found\r\n\r\nNot Found"


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8084))
server_socket.listen(1)
print("Веб-сервер запущен на http://localhost:8084")

while True:
    conn, addr = server_socket.accept()
    try:
        # Сначала читаем заголовки
        request_data = conn.recv(4096).decode('utf-8')

        # Парсим Content-Length из заголовков
        content_length = 0
        for line in request_data.split('\r\n'):
            if line.lower().startswith('content-length:'):
                content_length = int(line.split(':')[1].strip())
                break

        print(f"Content-Length из заголовков: {content_length}")

        # Если есть тело и мы его не получили полностью — дочитываем
        body_start = request_data.find('\r\n\r\n')
        if body_start != -1:
            received_body_len = len(request_data) - (body_start + 4)
        else:
            received_body_len = 0

        if content_length > received_body_len:
            missing = content_length - received_body_len
            print(f"Дочитываем ещё {missing} байт тела...")
            extra = conn.recv(missing).decode('utf-8')
            request_data += extra

        # Теперь обрабатываем полный запрос
        response = handle_request(request_data)
        conn.sendall(response)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()