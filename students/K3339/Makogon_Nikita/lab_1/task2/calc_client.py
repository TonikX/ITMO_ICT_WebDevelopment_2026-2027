import socket

HOST = '127.0.0.1'
PORT = 8082

def run_calc_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print("Решение квадратного уравнения ax^2 + bx + c = 0")
    a = input("Введите коэффициент a: ")
    b = input("Введите коэффициент b: ")
    c = input("Введите коэффициент c: ")

    payload = f"{a},{b},{c}"
    client_socket.sendall(payload.encode('utf-8'))

    response = client_socket.recv(1024).decode('utf-8')
    print(f"[РЕЗУЛЬТАТ ОТ СЕРВЕРА]: {response}")
    client_socket.close()

if __name__ == "__main__":
    run_calc_client()