import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 9090))
server.listen(1)

while True:
    conn, addr = server.accept()
    conn.recv(1024) 
    
    with open('index.html', 'r', encoding='utf-8') as file:
        html_body = file.read()
        
    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{html_body}"
    
    conn.send(response.encode('utf-8'))
    conn.close()