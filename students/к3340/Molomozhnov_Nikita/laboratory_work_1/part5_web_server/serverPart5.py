import socket
import json
import os
from urllib.parse import unquote_plus

DATA_FILE = 'grades.json'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5014))
server.listen(5)
print("Сервер запущен: http://127.0.0.1:5014")

while True:
    client, _ = server.accept()

    rfile = client.makefile('rb')
    request_line = rfile.readline().decode('iso-8859-1').rstrip('\r\n')
    parts = request_line.split(' ')
    method = parts[0]
    headers = {}
    while True:
        line = rfile.readline().decode('iso-8859-1').rstrip('\r\n')
        if line == '':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()

    body = ""
    if 'content-length' in headers:
        size = int(headers['content-length'])
        body = rfile.read(size).decode('utf-8')

    rfile.close()

    grades = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                grades = json.load(f)
        except:
            grades = {}

    if method == 'POST':
        form = {}
        for pair in body.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                form[unquote_plus(k)] = unquote_plus(v)

        subject = form.get('subject', '').strip()
        grade = form.get('grade', '').strip()

        if subject and grade.isdigit():
            if subject in grades:
                grades[subject].append(int(grade))
            else:
                grades[subject] = [int(grade)]

            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(grades, f, ensure_ascii=False, indent=2)

    rows = ""
    for subject in grades:
        marks = grades[subject]
        marks_str = ""
        for m in marks:
            marks_str += str(m) + " "
        rows += "<tr><td>" + subject + "</td><td>" + marks_str + "</td></tr>"

    if rows == "":
        rows = "<tr><td colspan='2'>Журнал пуст</td></tr>"

    html = "<!DOCTYPE html>"
    html += "<html><head><meta charset='UTF-8'><title>Журнал</title></head>"
    html += "<body>"
    html += "<h1>Журнал</h1>"
    html += "<form method='POST'>"
    html += "<input name='subject' placeholder='Дисциплина' required>"
    html += "<input name='grade' type='number' min='1' max='5' required>"
    html += "<button>Добавить</button>"
    html += "</form>"
    html += "<table border='1' cellpadding='8'>"
    html += "<tr><th>Дисциплина</th><th>Оценки</th></tr>"
    html += rows
    html += "</table>"
    html += "</body></html>"

    body_bytes = html.encode('utf-8')
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: text/html; charset=utf-8\r\n"
    response += "Content-Length: " + str(len(body_bytes)) + "\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"

    client.sendall(response.encode('utf-8') + body_bytes)
    client.close()