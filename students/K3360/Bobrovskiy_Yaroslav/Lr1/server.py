import socket

HOST = 'localhost'
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock: #Тип адреса (ipv4), тип подключения (udp)
    sock.bind((HOST, PORT))
    while True:
        raw_data, address = sock.recvfrom(1024) #размер буфера
        data = raw_data.decode()
        print(f'Client request: {data}, from: {address}')
        if data == 'Hello, server':
            response = 'Hello, client'
            print(f'Server response: {response}')
            sock.sendto(response.encode(), address)
        else:
            response = 'Huh?'
            print(f'Server response: {response}')
            sock.sendto(response.encode(), address)
