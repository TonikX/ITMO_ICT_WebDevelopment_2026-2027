import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8082))
server_socket.listen(1)
print("TCP сервер (площадь трапеции) запущен...")

while True:
    conn, addr = server_socket.accept()
    data = conn.recv(1024).decode('utf-8')
    if data:
        try:
            # Ожидаем три числа через запятую: "основание a,основание b,высота h"
            a, b, h = map(float, data.split(','))
            area = (a + b) / 2 * h
            conn.send(str(area).encode('utf-8'))
        except ValueError:
            conn.send("Ошибка: нужно ввести три числа".encode('utf-8'))
    conn.close()
