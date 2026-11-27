import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(('localhost', 45_001))
server.listen()

marks = dict()

def get(client):
    print('get')
    rows = ""
    for sub in marks:
        rows += f"<tr><td>{sub}</td><td>{marks[sub]}</td></tr>"
    html = f"""
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Оценки по дисциплинам</title>
</head>
<body>
    <h1>Оценки по дисциплинам</h1>
    <table border="1" cellpadding="6">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
</body>
</html>"""

    get_request_template = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(html.encode('utf-8'))}\r\n\r\n"
        f"{html}")

    client.send(get_request_template.encode('utf-8'))
    print('get correct')


def post(body, client):
    print('post')
    post_request_template = \
        (
        "HTTP/1.1 201 Created\r\n"
        "Content-Type: text/plain\r\n"
        f"Content-Length: {len("1".encode('utf-8'))}\r\n\r\n"
        "1"
    )
    buf = body.decode('utf-8').strip().split(' : ')
    if buf[0] in marks:
        marks[buf[0]].append(buf[1])
    else:
        marks[buf[0]] = [buf[1]]
    client.send(post_request_template.encode('utf-8'))
    print('post correct')


while True:
    client, address = server.accept()
    raw_request = client.recv(4096)
    if not raw_request:
        break
    headers, _, body = raw_request.partition(b'\r\n\r\n')
    if b'GET' in headers.split(b'\r\n')[0]:
        get(client)
    elif b'POST' in headers.split(b'\r\n')[0]:
        post(body, client)
    client.close()


