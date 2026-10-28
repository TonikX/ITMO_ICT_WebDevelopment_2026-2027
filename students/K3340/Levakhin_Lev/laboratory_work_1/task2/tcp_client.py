import socket

HOST = '127.0.0.1'
PORT = 9091

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"[Клиент] Подключён к {HOST}:{PORT}")

    try:
        while True:
            base_str = input("Введите основание параллелограмма (или 'exit' для выхода): ").strip()
            if base_str.lower() == 'exit':
                break
            height_str = input("Введите высоту параллелограмма: ").strip()

            message = f"{base_str} {height_str}"
            client_socket.sendall(message.encode('utf-8'))

            data = client_socket.recv(1024)
            if not data:
                print("[Клиент] Сервер закрыл соединение")
                break
            print(f"[Клиент] Ответ сервера: {data.decode('utf-8')}")
    finally:
        client_socket.close()
        print("[Клиент] Соединение закрыто")

if __name__ == '__main__':
    main()