import socket


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8082))
server_socket.listen(5)
print("HTTP-сервер запущен на http://localhost:8082")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read()

    html_bytes = html.encode("utf-8")

    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    response = headers.encode("utf-8") + html_bytes
    client_socket.sendall(response)
    client_socket.close()
