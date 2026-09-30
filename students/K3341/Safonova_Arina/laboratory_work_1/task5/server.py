import socket
from html import escape
from urllib.parse import parse_qs

journal = {}


def render_page():
    table_rows = ''
    for subject, scores in journal.items():
        table_rows += f'<tr><td>{escape(subject)}</td><td>{", ".join(map(str, scores))}</td></tr>\n'
    return f'''<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Журнал оценок</title></head>
<body>
<h1>Журнал оценок</h1>
<form method="post" action="/">
    <label>Дисциплина <input name="subject" required></label>
    <label>Оценка <input name="grade" type="number" required></label>
    <button type="submit">Добавить</button>
</form>

<table border="1">
<tr><th>Дисциплина</th><th>Оценки</th></tr>
{table_rows}
</table>
</body>
</html>'''


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 8005))
    server_socket.listen()
    print('Откройте http://127.0.0.1:8005', flush=True)

    while True:
        peer, peer_address = server_socket.accept()
        with peer:
            peer.settimeout(5)
            try:
                with peer.makefile('rb') as incoming:
                    start_line = incoming.readline()
                    if not start_line:
                        continue
                    method, path, version = start_line.decode().split()
                    headers = {}
                    while True:
                        line = incoming.readline()
                        if line in (b'\r\n', b'\n', b''):
                            break
                        key, value = line.decode().split(':', 1)
                        headers[key.lower()] = value.strip()

                    if method == 'POST':
                        body = incoming.read(int(headers['content-length']))
                        form = parse_qs(body.decode('utf-8'))
                        subject = form['subject'][0]
                        grade = int(form['grade'][0])
                        journal.setdefault(subject, []).append(grade)

                    if method in ('GET', 'POST'):
                        content = render_page().encode('utf-8')
                        headers = (
                            'HTTP/1.1 200 OK\r\n'
                            'Content-Type: text/html; charset=utf-8\r\n'
                            f'Content-Length: {len(content)}\r\n'
                            'Connection: close\r\n\r\n'
                        )
                        peer.sendall(headers.encode() + content)
            except OSError:
                pass
