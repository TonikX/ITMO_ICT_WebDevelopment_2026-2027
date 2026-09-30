import socket
import math

HOST = '127.0.0.1'
PORT = 12345

def calculate(variant, params):
    try:
        if variant == 1:  # Теорема Пифагора
            a, b = map(float, params)
            c = math.sqrt(a**2 + b**2)
            return f"Гипотенуза c = {c:.2f}"
        
        elif variant == 2:  # Квадратное уравнение
            a, b, c = map(float, params)
            d = b**2 - 4 * a * c
            if d < 0:
                return "Корней нет (D < 0)"
            elif d == 0:
                x = -b / (2 * a)
                return f"Корень x = {x:.2f}"
            else:
                x1 = (-b + math.sqrt(d)) / (2 * a)
                x2 = (-b - math.sqrt(d)) / (2 * a)
                return f"Корни: x1 = {x1:.2f}, x2 = {x2:.2f}"
                
        elif variant == 3:  # Площадь трапеции
            a, b, h = map(float, params)
            s = ((a + b) / 2) * h
            return f"Площадь трапеции S = {s:.2f}"
            
        elif variant == 4:  # Площадь параллелограмма
            a, h = map(float, params)
            s = a * h
            return f"Площадь параллелограмма S = {s:.2f}"
            
        else:
            return "Неизвестный номер варианта."
    except Exception as e:
        return f"Ошибка при расчёте: {e}"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"TCP Математический сервер запущен на {HOST}:{PORT}...")

while True:
    conn, addr = server_socket.accept()
    data = conn.recv(1024).decode('utf-8')
    if data:
        parts = data.strip().split()
        variant = int(parts[0])
        params = parts[1:]
        result = calculate(variant, params)
        conn.send(result.encode('utf-8'))
    conn.close()