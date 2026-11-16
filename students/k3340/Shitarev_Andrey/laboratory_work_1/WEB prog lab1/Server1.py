import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9090))
print("UDP сервер запущен")

while True:
    data, client_info = sock.recvfrom(1024)
    if not data:
        break

    client_message = data.decode('utf-8')
    print(f"Соббщение от {client_info} - {client_message}")

    response = "Hello, client"
    sock.sendto(response.encode('utf-8'), client_info)

sock.close()
input()


