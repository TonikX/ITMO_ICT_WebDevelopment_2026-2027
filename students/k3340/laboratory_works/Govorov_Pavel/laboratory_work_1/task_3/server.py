import socket

with open("index.html", "rb") as file:
    html = file.read()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen()
print("HTTP server: http://127.0.0.1:8080")

while True:
    connection, _ = server.accept()
    connection.recv(1024)
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        + f"Content-Length: {len(html)}\r\n\r\n".encode()
        + html
    )
    connection.sendall(response)
    connection.close()
