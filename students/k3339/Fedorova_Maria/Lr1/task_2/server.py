import socket


HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print(f"TCP-сервер запущен на {HOST}:{PORT}")
        print("Ожидание подключения клиента...")

        connection, client_address = server_socket.accept()

        with connection:
            print(f"Клиент подключён: {client_address}")

            data = connection.recv(BUFFER_SIZE).decode("utf-8")
            base, height = map(float, data.split())

            print(f"Получено основание: {base}")
            print(f"Получена высота: {height}")

            area = base * height

            response = str(area)
            connection.sendall(response.encode("utf-8"))

            print(f"Площадь параллелограмма: {area}")
            print("Результат отправлен клиенту")


if __name__ == "__main__":
    main()