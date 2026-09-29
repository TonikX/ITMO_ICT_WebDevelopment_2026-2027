import socket
import threading

# Список активных клиентов и блокировка для безопасного изменения из потоков
clients = []
clients_lock = threading.Lock()


def handle_client(conn, addr):
    print(f"[{addr}] подключился.")
    try:
        while True:
            message = conn.recv(1024).decode('utf-8')
            if not message: break

            # Рассылаем сообщение всем, кроме отправителя
            with clients_lock:
                for client in clients:
                    if client != conn:
                        try:
                            client.sendall(message.encode('utf-8'))
                        except:
                            pass  # Если клиент отвалился, пропускаем
    except:
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[{addr}] отключился.")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8083))
server_socket.listen()
print("Чат-сервер запущен...")

while True:
    conn, addr = server_socket.accept()
    with clients_lock:
        clients.append(conn)

    # Запускаем поток для обработки конкретного клиента
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()