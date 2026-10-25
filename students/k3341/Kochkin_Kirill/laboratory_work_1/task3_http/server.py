import socket

# 127.0.0.1:8080
HOST = "127.0.0.1"
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
with open("index.html", "r", encoding="utf-8") as file:
    html = file.read()
print(f"HTTP сервер запущен на {HOST}:{PORT}...")

while True:
    client_socket, client_address = server_socket.accept()
    request = client_socket.recv(1024)
    html_bytes = html.encode("utf-8")

    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "\r\n"
    )

    response = headers.encode("utf-8") + html_bytes

    client_socket.sendall(response)
    client_socket.close()

