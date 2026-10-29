import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Сервер запущен: http://{HOST}:{PORT}")

while True:
    connection, client_address = server_socket.accept()

    print("Клиент подключен:", client_address)

    request = connection.recv(4096)

    print("HTTP-запрос:")
    print(request.decode("utf-8", errors="ignore"))

    html_path = Path(__file__).parent / "index.html"

    with open(html_path, "r", encoding="utf-8") as file:
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

    connection.sendall(response)
    connection.close()