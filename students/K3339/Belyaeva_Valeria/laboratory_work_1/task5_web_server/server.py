import html
import socket
import urllib.parse

# Хранилище: {'Математика': ['5', '4'], 'Физика': ['5']}
grades_journal = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8085))
server_socket.listen(1)
print("Сервер журнала запущен на http://127.0.0.1:8085")

def render_html():
    page = """
    <html><head><meta charset='utf-8'><title>Журнал оценок</title></head>
    <body>
        <h2>Добавить оценку</h2>
        <form method='POST'>
            <input type='text' name='subject' placeholder='Дисциплина' required>
            <input type='text' name='grade' placeholder='Оценка' required>
            <button type='submit'>Сохранить</button>
        </form>
        <h2>Журнал:</h2><ul>
    """
    for subject, grades in grades_journal.items():
        # html.escape - чтобы введённый текст не превратился в HTML-теги
        page += f"<li><b>{html.escape(subject)}</b>: {html.escape(', '.join(grades))}</li>"
    page += "</ul></body></html>"
    return page

while True:
    conn, addr = server_socket.accept()
    request = conn.recv(4096)

    if not request:
        conn.close()
        continue

    # Парсим HTTP-запрос: заголовки отделены от тела пустой строкой
    headers_part, _, body = request.partition(b'\r\n\r\n')
    lines = headers_part.decode('utf-8').split('\r\n')
    method = lines[0].split()[0]

    if method == 'POST':
        # Узнаем длину тела из заголовка Content-Length
        content_length = 0
        for line in lines[1:]:
            if line.lower().startswith('content-length:'):
                content_length = int(line.split(':')[1])

        # Браузер может прислать тело отдельным пакетом - дочитываем его
        while len(body) < content_length:
            body += conn.recv(4096)

        data = urllib.parse.parse_qs(body.decode('utf-8'))
        subject = data.get('subject', [''])[0].strip()
        grade = data.get('grade', [''])[0].strip()

        if subject and grade:
            if subject not in grades_journal:
                grades_journal[subject] = []
            grades_journal[subject].append(grade)

    html_content = render_html()
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(html_content.encode('utf-8'))}\r\n"
        "Connection: close\r\n\r\n"
        f"{html_content}"
    )

    conn.sendall(response.encode('utf-8'))
    conn.close()
