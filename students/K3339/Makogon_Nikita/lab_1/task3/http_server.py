import socket
import os

HOST = '127.0.0.1'
PORT = 8083

def run_http_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[HTTP СЕРВЕР] Доступен по адресу: http://{HOST}:{PORT}")

    while True:
        client_conn, client_addr = server_socket.accept()
        try:
            request = client_conn.recv(1024).decode('utf-8')
            print(f"[HTTP] Запрос от {client_addr}")

            if os.path.exists("index.html"):
                with open("index.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html; charset=UTF-8\r\n"
                    f"Content-Length: {len(html_content.encode('utf-8'))}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    + html_content
                )
            else:
                body = "<h1>404 Not Found</h1><p>File index.html not found.</p>"
                response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/html; charset=UTF-8\r\n"
                    f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    + body
                )

            client_conn.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"[HTTP ОШИБКА]: {e}")
        finally:
            client_conn.close()

if __name__ == "__main__":
    run_http_server()