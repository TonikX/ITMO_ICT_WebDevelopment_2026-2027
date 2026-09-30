import socket


SERVER_ADDRESS = ("127.0.0.1", 5001)
BUFFER_SIZE = 1024


def main() -> None:
    print("Решение квадратного уравнения ax² + bx + c = 0")
    a = input("Введите коэффициент a: ")
    b = input("Введите коэффициент b: ")
    c = input("Введите коэффициент c: ")

    request = f"{a};{b};{c}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(SERVER_ADDRESS)
        client_socket.sendall(request.encode("utf-8"))

        data = client_socket.recv(BUFFER_SIZE)
        response = data.decode("utf-8")
        print(f"Ответ сервера: {response}")


if __name__ == "__main__":
    main()
