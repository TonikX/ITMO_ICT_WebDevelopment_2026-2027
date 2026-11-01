import socket
import math

HOST = '127.0.0.1'
PORT = 8082

def solve_quadratic(a, b, c):
    if a == 0:
        if b == 0:
            return "Нет решений (корректных)" if c != 0 else "Бесконечно много решений"
        return f"Линейное уравнение, корень: x = {-c / b}"
    
    discriminant = b**2 - 4*a*c
    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        return f"Два корня: x1 = {x1:.2f}, x2 = {x2:.2f}"
    elif discriminant == 0:
        x = -b / (2 * a)
        return f"Один корень: x = {x:.2f}"
    else:
        real = -b / (2 * a)
        imag = math.sqrt(abs(discriminant)) / (2 * a)
        return f"Комплексные корни: x1 = {real:.2f} + {imag:.2f}i, x2 = {real:.2f} - {imag:.2f}i"

def run_calc_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[TCP КАЛЬКУЛЯТОР] Сервер запущен на {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        print(f"[TCP КАЛЬКУЛЯТОР] Подключение от {addr}")
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                continue
            parts = list(map(float, data.split(',')))
            if len(parts) != 3:
                conn.sendall(b"Error: Need 3 coefficients (a,b,c)")
                continue
            a, b, c = parts
            result = solve_quadratic(a, b, c)
            conn.sendall(result.encode('utf-8'))
        except Exception as e:
            conn.sendall(f"Error: {str(e)}".encode('utf-8'))
        finally:
            conn.close()

if __name__ == "__main__":
    run_calc_server()