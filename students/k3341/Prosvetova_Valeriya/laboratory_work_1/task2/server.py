import socket

HOST = 'localhost'
PORT = 9002


def parallelogram_area(base: float, height: float) -> float:
    """Вычисляет площадь параллелограмма по основанию и высоте."""
    return base * height


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"TCP-сервер (площадь параллелограмма) запущен на {HOST}:{PORT}...")

while True:
    conn, addr = server_socket.accept()
    print(f"Подключение от {addr}")

    data = conn.recv(1024).decode()
    print(f"Получены параметры: {data}")

    try:
        base_str, height_str = data.split(',')
        base, height = float(base_str), float(height_str)
        if base <= 0 or height <= 0:
            raise ValueError("основание и высота должны быть положительными")
        area = parallelogram_area(base, height)
        result = f"Площадь параллелограмма: {area:.4f}"
    except ValueError as exc:
        result = f"Ошибка в данных: {exc}"

    conn.sendall(result.encode())
    conn.close()
