import socket 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))

server_socket.listen(5)
print("HTTP сервер запущен...")

while True:
    client_connection, client_address = server_socket.accept()
    print(f'Подключение от {client_address}')

    request = client_connection.recv(4096).decode()
    print(f'Запрос клиента:\n{request}')

    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read()
    html_response = html.encode()
    http_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_response)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode()

    fin_answer = http_headers + html_response
    client_connection.sendall(fin_answer) 
    client_connection.close()