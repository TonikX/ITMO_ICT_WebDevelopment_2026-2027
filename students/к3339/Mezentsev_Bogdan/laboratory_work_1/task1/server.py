import socket


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    server_socket.bind(("localhost", 8080))
    print(f"UDP-сервер запущен на порту 8080")

    try:
        while True:
            data, client_address = server_socket.recvfrom(1024)
            message = data.decode("utf-8")

            print(f"Сообщение от {client_address}: {message}")

            response = "Hello, client"
            server_socket.sendto(response.encode("utf-8"), client_address)
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
