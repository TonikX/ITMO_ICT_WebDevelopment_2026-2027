import socket

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # говорим, что это tcp-сервер


def pythagorean_theorem(data):
    a, b = map(float, data.split())
    c = (a ** 2 + b ** 2) ** 0.5
    return c


server_sock.bind(('', 8080))  # порт 8080 на всех доступных интерфейсах
server_sock.listen(1)

while True:
    conn, addr = server_sock.accept()
    print(f"{addr} is connected")
    # считываем данные клиента
    data = conn.recv(1024)
    print(f"Полученные данные от пользователя: {data.decode('utf-8')}")
    if not data:
        break

    conn.send(str(pythagorean_theorem(data)).encode('utf-8'))
    print('Сервер останавливается')
    conn.close()
