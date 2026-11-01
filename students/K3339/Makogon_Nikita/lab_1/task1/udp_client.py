import socket

HOST = '127.0.0.1'
PORT = 8081

def run_udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = "Hello, server"
    
    print(f"[UDP КЛИЕНТ] Отправка: {message}")
    client_socket.sendto(message.encode('utf-8'), (HOST, PORT))

    data, server_address = client_socket.recvfrom(1024)
    print(f"[UDP КЛИЕНТ] Ответ от сервера: {data.decode('utf-8')}")
    client_socket.close()

if __name__ == "__main__":
    run_udp_client()