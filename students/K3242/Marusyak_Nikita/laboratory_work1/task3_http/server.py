import socket

HOST = "127.0.0.1"
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind((HOST, PORT))

server_socket.listen(5)

print(f"HTTP-сервер запущен:")
print(f"http://{HOST}:{PORT}")

while True:

    client_socket, client_address = server_socket.accept()

    request = client_socket.recv(1024).decode("utf-8")

    print("Получен HTTP-запрос:")
    print(request)

    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read()

    html_bytes = html.encode("utf-8")

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + html_bytes

    client_socket.sendall(response)

    client_socket.close()
