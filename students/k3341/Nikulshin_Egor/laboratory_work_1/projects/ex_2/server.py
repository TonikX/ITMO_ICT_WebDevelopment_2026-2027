
import socket

HOST = "127.0.0.1"
PORT = 5000

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind((HOST, PORT))

server_socket.listen(1)

print("Сервер ожидает подключения...")

while True:
    conn, addr = server_socket.accept()

    print(f"Подключен клиент: {addr}")

    try:
        data = conn.recv(1024).decode("utf-8")

        a, b, h = map(float, data.split())

        area = ((a + b) * h) / 2

        conn.send(str(round(area, 2)).encode("utf-8"))

        print(f"Площадь трапеции: {area}")

    except ValueError:
        conn.send("Ошибка вычисления".encode("utf-8"))

    finally:
        conn.close()
