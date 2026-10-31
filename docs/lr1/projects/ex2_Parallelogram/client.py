import socket

HOST = "127.0.0.1"
PORT = 5000

client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client_socket.connect((HOST, PORT))

try:
    a = float(input("Введите основание параллелограмма: "))

    if a <= 0:
        print("Ошибка: основание должно быть положительным")
        client_socket.close()
        exit()

    h = float(input("Введите высоту параллелограмма: "))

    if h <= 0:
        print("Ошибка: высота должна быть положительной")
        client_socket.close()
        exit()

    message = f"{a} {h}"

    client_socket.send(message.encode("utf-8"))

    data = client_socket.recv(1024).decode("utf-8")

    print(f"Площадь параллелограмма: {data}")

except ValueError:
    print("Ошибка: необходимо ввести число")

finally:
    client_socket.close()