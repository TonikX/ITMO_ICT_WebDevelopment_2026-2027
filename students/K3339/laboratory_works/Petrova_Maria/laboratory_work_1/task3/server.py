import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 8082))
server_socket.listen(1)

client_socket, client_address = server_socket.accept()
request = client_socket.recv(1024)

with open("index.html", "r", encoding="utf-8") as file:
    html = file.read()

body = html.encode("utf-8")

response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    f"Content-Length: {len(body)}\r\n"
    "\r\n"
).encode("utf-8") + body

client_socket.sendall(response)

client_socket.close()
server_socket.close()