import socket

HOST = '127.0.0.1'
PORT = 8081

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[TCP Server] Ожидание подключения на {HOST}:{PORT}...")

    conn, addr = server_socket.accept()
    with conn:
        print(f"[TCP Server] Подключен клиент: {addr}")

        data = conn.recv(1024).decode('utf-8')
        print(f"[TCP Server] Получены данные: {data}")

        try:
            a, h = map(float, data.split())
            area = a * h
            result = f"Площадь параллелограмма: {area}"
        except ValueError:
            result = "Ошибка: введите два числа (основание и высоту) через пробел."

        conn.sendall(result.encode('utf-8'))
        print(f"[TCP Server] Отправлен результат: {result}")
