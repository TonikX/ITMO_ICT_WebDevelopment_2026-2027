import socket

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"HTTP-сервер запущен на http://{HOST}:{PORT}")

while True:
    client_socket, _ = server_socket.accept()
    request = client_socket.recv(1024).decode('utf-8')

    try:
        with open('index.html', 'rb') as f:
            body = f.read()
        
        response_header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
        )
        client_socket.sendall(response_header.encode('utf-8') + body)
    except FileNotFoundError:
        body = "<h1>404 File Not Found</h1>".encode('utf-8')
        response_header = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
        )
        client_socket.sendall(response_header.encode('utf-8') + body)

    client_socket.close()