
import socket

HOST = "127.0.0.1"
PORT = 5000

client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client_socket.connect((HOST, PORT))

try:
    a = float(input("Введите первое основание трапеции: "))

    if a <= 0:
        print("Ошибка: основание должно быть положительным")
        client_socket.close()
        exit()

    b = float(input("Введите второе основание трапеции: "))

    if b <= 0:
        print("Ошибка: основание должно быть положительным")
        client_socket.close()
        exit()

    h = float(input("Введите высоту трапеции: "))

    if h <= 0:
        print("Ошибка: высота должна быть положительной")
        client_socket.close()
        exit()

    message = f"{a} {b} {h}"

    client_socket.send(message.encode("utf-8"))

    data = client_socket.recv(1024).decode("utf-8")

    print(f"Площадь трапеции: {data}")

except ValueError:
    print("Ошибка: необходимо ввести число")

finally:
    client_socket.close()
