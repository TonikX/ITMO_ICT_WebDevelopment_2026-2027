import socket

SERVER = ("localhost", 8080)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(5)

client_socket.sendto("Hello, server".encode("utf-8"), SERVER)

try:
    data, _ = client_socket.recvfrom(1024)
    print(f"Ответ от сервера: {data.decode('utf-8')}")
except socket.timeout:
    print("Сервер не ответил за 5 секунд (запущен ли server.py?)")
except ConnectionResetError:
    print("Сервер недоступен: порт закрыт. Сначала запустите server.py.")
finally:
    client_socket.close()