import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 30_002))
server.listen()

while True:
    socket_for_client, addr = server.accept()

    with open('index.html', 'r') as file:
        html = file.read().encode('utf-8')

    headers = "HTTP/1.1 200 OK\r\n" \
            "Content-Type: text/html\r\n" \
            f"Content-Length: {len(html)}\r\n" \
            "\r\n".encode('utf-8')

    socket_for_client.send(headers + html)

    socket_for_client.close()