import socket

HOST = '127.0.0.1'
PORT = 9091

def calculate_parallelogram_area(base: float, height: float) -> float:
    """Площадь параллелограмма: S = a * h"""
    return base * height

def handle_client(conn, addr):
    print(f"[Сервер] Подключён клиент {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                # Клиент закрыл соединение
                print(f"[Сервер] Клиент {addr} отключился")
                break

            message = data.decode('utf-8').strip()
            print(f"[Сервер] Получено от {addr}: {message}")

            # Ожидаем два числа через пробел
            try:
                parts = message.split()
                if len(parts) != 2:
                    raise ValueError("Нужно ровно два числа")
                base = float(parts[0])
                height = float(parts[1])
            except ValueError as e:
                error_msg = f"Ошибка: некорректный ввод ({e}). Пришлите два числа через пробел"
                conn.sendall(error_msg.encode('utf-8'))
                continue

            if base <= 0 or height <= 0:
                conn.sendall("Ошибка: стороны должны быть положительными.".encode('utf-8'))
                continue

            area = calculate_parallelogram_area(base, height)
            response = f"Площадь параллелограмма: {area}"
            conn.sendall(response.encode('utf-8'))
            print(f"[Сервер] Отправлено: {response}")
    finally:
        conn.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Позволяет переиспользовать порт сразу после закрытия сервера
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # очередь до 5 подключений
    print(f"[Сервер] Запущен на {HOST}:{PORT}, ждём подключений...")

    while True:
        conn, addr = server_socket.accept()
        handle_client(conn, addr)

if __name__ == '__main__':
    main()