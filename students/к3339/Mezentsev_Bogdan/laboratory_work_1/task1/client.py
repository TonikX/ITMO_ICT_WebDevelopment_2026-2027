import socket


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
    message = "Hello, server"
    client_socket.sendto(message.encode("utf-8"), ("localhost", 8080))
    print(f"Сообщение отправлено серверу: {message}")

    data, server_address = client_socket.recvfrom(1024)
    response = data.decode("utf-8")
    print(f"Ответ от {server_address}: {response}")
