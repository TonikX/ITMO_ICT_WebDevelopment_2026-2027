import socket
import os

def read_html_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "<h1>404 - Файл не найден</h1>"

def create_http_response(content, status_code=200):
    status_messages = {
        200: "OK",
        404: "Not Found"
    }
    
    status_line = f"HTTP/1.1 {status_code} {status_messages[status_code]}"
    headers = [
        f"Content-Type: text/html; charset=utf-8",
        f"Content-Length: {len(content.encode('utf-8'))}",
        "Connection: close"
    ]
    
    response = status_line + "\r\n"
    response += "\r\n".join(headers) + "\r\n"
    response += "\r\n" + content
    
    return response.encode('utf-8')

def run_http_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(5)
    
    print("HTTP Сервер запущен на порту 8080: http://localhost:8080")
    
    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Подключен клиент: {address}")
            
            content = read_html_file('index.html')
            
            response = create_http_response(content)
            
            client_socket.sendall(response)
            client_socket.close()
            print(f"Отправлен ответ клиенту: {address}")
            
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_http_server()