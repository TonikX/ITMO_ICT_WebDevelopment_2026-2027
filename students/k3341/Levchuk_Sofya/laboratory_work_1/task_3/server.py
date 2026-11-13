import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(("localhost", 8080))

server_socket.listen(5)
print("HTTP-сервер запущен на http://localhost:8080")

client_connection, client_address = server_socket.accept()
print(f"подключение от клиента: {client_address}")

request = client_connection.recv(1024).decode()
print(f"получен запрос от клиента: \n{request}")

with open("index.html", "r", encoding="utf-8") as file:
    html_content = file.read()

content_length = len(html_content.encode())

http_response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=UTF-8\r\n"
    f"Content-Length: {content_length}\r\n"
    "Connection: close\r\n"
    "\r\n"
    + html_content
)

client_connection.sendall(http_response.encode())

client_connection.close()
server_socket.close()
print("работа сервера завершена")