import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("127.0.0.1", 5003)
server_socket.bind(server_address)

server_socket.listen()

client_socket, client_address = server_socket.accept()

request = client_socket.recv(1024)
print(request.decode())

with open("index.html", "r", encoding="utf-8") as file:
    html = file.read()

html_bytes = html.encode("utf-8")
content_length = len(html_bytes)

response_headers = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=utf-8\r\n"
    f"Content-Length: {content_length}\r\n"
    "\r\n"
)

response = response_headers.encode("utf-8") + html_bytes

client_socket.sendall(response)

client_socket.close()
server_socket.close()