import socket

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket_server.bind(('localhost', 8080))

socket_server.listen(1)

print('Server is listening on port 8080...')

while True:
    client_connection, address = socket_server.accept()

    request = b''

    while b'\r\n\r\n' not in request:
        chunk = client_connection.recv(1024)
        
        if chunk == b'':
            break
        
        request += chunk

    if b'\r\n\r\n' not in request:
        client_connection.close()
    
    with open('index.html', 'rb') as file:
        body = file.read()
    
    response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: ' + str(len(body)).encode() + b'\r\nConnection: close\r\n\r\n'
    
    response = response + body
    
    client_connection.sendall(response)
    print(f'Received request from {address}: {request.decode("utf-8")}')
    
    client_connection.close()

    break

socket_server.close()