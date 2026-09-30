import math
import socket

HOST, PORT = "localhost", 8080


def pythagoras(a, b):
    """Теорема Пифагора: по катетам a и b находит гипотенузу c."""
    if a <= 0 or b <= 0:
        raise ValueError("катеты должны быть положительными")
    return f"Гипотенуза c = {math.hypot(a, b):g}"


def process(request: str) -> str:
    try:
        values = [float(x.replace(",", ".")) for x in request.split()]
        if len(values) != 2:
            return f"Ошибка: нужно 2 числа, получено {len(values)}"
        return pythagoras(*values)
    except ValueError as e:
        return f"Ошибка: {e}"


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"TCP-сервер запущен на {HOST}:{PORT}...")

while True:
    conn, addr = server_socket.accept()
    print(f"Подключение от {addr}")
    request = conn.recv(1024).decode("utf-8")
    print(f"Параметры: {request}")
    response = process(request)
    print(f"Результат: {response}")
    conn.sendall(response.encode("utf-8"))
    conn.close()
