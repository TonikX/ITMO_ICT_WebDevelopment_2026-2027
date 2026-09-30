import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen(1)

print(f"Сервер запущен: http://127.0.0.1:8080")

while 1:
    connection, address = server.accept()
    print("Клиент подключился")

    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read()

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(html.encode('utf-8'))}\r\n"
        "\r\n"
        + html
    )
    connection.sendall(response.encode("utf-8"))
    connection.close()

