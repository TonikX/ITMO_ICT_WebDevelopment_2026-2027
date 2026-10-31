import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5012))
server.listen(1)
print("http://127.0.0.1:5012")

while True:
    client_socket, client_address = server.accept()
    request = client_socket.recv(1024).decode('utf-8')
    print("запрос клиента")
    print(request)
    print("конец запроса")

    try:
        with open('index.html', 'rb') as f:
            body = f.read()

        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        client_socket.send(headers.encode('utf-8') + body)
        print(f"Отправлено {len(body)} байт HTML")

    except FileNotFoundError:
        error_body = b"<h1>404 Not Found</h1>"
        headers = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(error_body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        client_socket.send(headers.encode('utf-8') + error_body)
        print("index.html не найден")

    client_socket.close()