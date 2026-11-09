import socket
import json
import os
from urllib.parse import unquote

HOST = '127.0.0.1'
PORT = 8084

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRADES_FILE = os.path.join(BASE_DIR, 'grades.json')
GRADES_HTML = os.path.join(BASE_DIR, 'grades.html')
SUCCESS_HTML = os.path.join(BASE_DIR, 'success.html')

grades = {}


def load_grades():
    """
    Загружает оценки из файла grades.json при запуске сервера.
    """
    global grades

    if os.path.exists(GRADES_FILE):
        try:
            with open(GRADES_FILE, 'r', encoding='utf-8') as f:
                grades = json.load(f)
            print(f"[Server] Загружено оценок из файла: {len(grades)} дисциплин")
        except Exception as e:
            print(f"[Server] Ошибка чтения файла: {e}")
            grades = {}
    else:
        print("[Server] Файл grades.json не найден, начинаем с пустым журналом")


def save_grades():
    """
    Сохраняет текущие оценки в файл grades.json.
    Вызывается после каждого добавления новой оценки.
    """
    try:
        with open(GRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump(grades, f, ensure_ascii=False, indent=2)
        print(f"[Server] Оценки сохранены в файл")
    except Exception as e:
        print(f"[Server] Ошибка сохранения: {e}")


def read_template(filepath):
    """
    Читает HTML-файл и возвращает его содержимое как строку.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<h1>Ошибка: шаблон {filepath} не найден</h1>"


def generate_grades_html():
    """
    Генерирует основную страницу журнала оценок.
    Читает шаблон grades.html и подставляет в него таблицу с оценками.
    """
    template = read_template(GRADES_HTML)

    if grades:
        table_html = "<table border='1' cellpadding='5' cellspacing='0'>\n"
        table_html += "<tr><th>Дисциплина</th><th>Оценки</th></tr>\n"

        for subject, marks in grades.items():
            table_html += f"<tr><td>{subject}</td><td>{', '.join(marks)}</td></tr>\n"

        table_html += "</table>"
    else:
        table_html = "<p>Пока нет оценок.</p>"

    final_html = template.replace('{{GRADES_TABLE}}', table_html)

    return final_html


def generate_success_html(subject, grade):
    """
    Генерирует страницу подтверждения после добавления оценки.
    Читает шаблон success.html и подставляет в него название дисциплины и оценку.
    """
    template = read_template(SUCCESS_HTML)

    final_html = template.replace('{{SUBJECT}}', subject)
    final_html = final_html.replace('{{GRADE}}', grade)

    return final_html


def parse_request(request_data):
    """
    Разбирает HTTP-запрос на составные части.
    возвращаем: метод (POST), путь (/), тело (subject=Физика&grade=4)
    """
    headers, _, body = request_data.partition('\r\n\r\n')

    first_line = headers.split('\r\n')[0]

    parts = first_line.split(' ')
    method = parts[0]
    path = parts[1]

    return method, path, body


def parse_post_body(body):
    """
    Разбирает тело POST-запроса.

    Превращает тело (например: subject=Физика&grade=4)
    в словарь (например: {"subject": "Физика", "grade": "4"})
    """
    params = {}

    for param in body.split('&'):
        key, value = param.split('=', 1)

        params[key] = unquote(value)

    return params


def send_response(conn, status_code, status_text, content_type, body):
    """
    Формирует и отправляет HTTP-ответ.
    """
    body_bytes = body.encode('utf-8')

    headers = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    conn.sendall(headers.encode('utf-8') + body_bytes)


def handle_client(conn):
    """
    Обрабатывает один HTTP-запрос от клиента.
    """
    try:
        request_data = conn.recv(4096).decode('utf-8')

        if not request_data:
            return

        method, path, body = parse_request(request_data)
        print(f"[Server] Получен запрос: {method} {path}")

        if method == 'GET':
            html = generate_grades_html()

            send_response(conn, 200, 'OK', 'text/html; charset=utf-8', html)
            print(f"[Server] Отдана страница журнала")

        elif method == 'POST':
            params = parse_post_body(body)

            subject = params.get('subject', 'Неизвестно')
            grade = params.get('grade', 'Неизвестно')

            if subject not in grades:
                grades[subject] = []
            grades[subject].append(grade)

            save_grades()

            print(f"[Server] Добавлена оценка: {subject} - {grade}")

            html = generate_success_html(subject, grade)

            send_response(conn, 200, 'OK', 'text/html; charset=utf-8', html)
            print(f"[Server] Отдана страница подтверждения")

        else:
            error_html = "<h1>405 Method Not Allowed</h1><p>Поддерживаются только GET и POST</p>"
            send_response(conn, 405, 'Method Not Allowed', 'text/html; charset=utf-8', error_html)
            print(f"[Server] Неизвестный метод: {method}")

    except Exception as e:
        print(f"[Server] Ошибка обработки запроса: {e}")
    finally:
        conn.close()
        print(f"[Server] Соединение закрыто")


load_grades()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))

    server_socket.listen(5)

    print(f"[Web Server] Сервер запущен на http://{HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        print(f"[Server] Новое подключение от {addr}")

        handle_client(conn)
