import socket


HOST = "localhost"
PORT = 8080


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))

server_socket.listen(5)

print(f"HTTP-сервер запущен: http://{HOST}:{PORT}")


while True:
    client_socket, client_address = server_socket.accept()

    print(f"Подключение от {client_address}")

    request = client_socket.recv(1024).decode("utf-8")
    print(f"Запрос клиента:\n{request}")

    try:
        with open("../../files/index.html", "r", encoding="utf-8") as file:
            html_content = file.read()

        html_bytes = html_content.encode("utf-8")

        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(html_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("utf-8") + html_bytes

    except FileNotFoundError:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>404 Not Found</title>
        </head>
        <body>
            <h1>404 Not Found</h1>
            <p>Файл index.html не найден.</p>
        </body>
        </html>
        """

        html_bytes = html_content.encode("utf-8")

        http_response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(html_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("utf-8") + html_bytes

    client_socket.sendall(http_response)

    client_socket.close()