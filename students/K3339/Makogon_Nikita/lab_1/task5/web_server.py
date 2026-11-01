import socket
from urllib.parse import parse_qs

HOST = '127.0.0.1'
PORT = 8085

# Структура данных для журнала оценок, сгруппированная по дисциплинам
grades_db = {
    "Математический анализ": [5, 4],
    "Веб-программирование": [5]
}

def render_html():
    items_html = ""
    for discipline, grades in grades_db.items():
        grades_str = ", ".join(map(str, grades))
        items_html += f"<li><b>{discipline}</b>: Оценки: [{grades_str}]</li>"
    
    if not items_html:
        items_html = "<li>Журнал пока пуст.</li>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Журнал оценок</title>
    </head>
    <body>
        <h1>Журнал успеваемости студентов</h1>
        <ul>
            {items_html}
        </ul>
        <hr>
        <h2>Добавить оценку</h2>
        <form method="POST" action="/">
            <label>Дисциплина: <input type="text" name="discipline" required></label><br><br>
            <label>Оценка (число): <input type="number" name="grade" min="1" max="5" required></label><br><br>
            <button type="submit">Отправить</button>
        </form>
    </body>
    </html>
    """

def run_web_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[ВЕБ-СЕРВЕР ЖУРНАЛА] Запущен: http://{HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        try:
            request_data = conn.recv(4096).decode('utf-8')
            if not request_data:
                conn.close()
                continue

            lines = request_data.split('\r\n')
            request_line = lines[0]
            method, path, _ = request_line.split(' ')

            if method == 'POST':
                # Ищем тело POST-запроса после пустой строки
                body_index = request_data.find('\r\n\r\n')
                if body_index != -1:
                    body = request_data[body_index+4:]
                    parsed_body = parse_qs(body)
                    discipline = parsed_body.get('discipline', [''])[0].strip()
                    grade_str = parsed_body.get('grade', [''])[0].strip()

                    if discipline and grade_str.isdigit():
                        grade = int(grade_str)
                        if discipline in grades_db:
                            grades_db[discipline].append(grade)
                        else:
                            grades_db[discipline] = [grade]

            html_content = render_html()
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                f"Content-Length: {len(html_content.encode('utf-8'))}\r\n"
                "Connection: close\r\n"
                "\r\n"
                + html_content
            )
            conn.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"[ОШИБКА ВЕБ-СЕРВЕРА]: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    run_web_server()