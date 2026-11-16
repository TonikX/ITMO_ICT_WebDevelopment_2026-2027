from pydoc import cli
import socket
import threading

HOST = ''
PORT = 9080

clients = []
nicknames = []

def send_to_all(message, sender_socket = None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                pass # если сокет почему-то не работает

def for_one_client(client_socket):
    try:
        client_socket.send("Nickname_Request".encode('utf-8'))
        nickname = client_socket.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client_socket)
        print(f"Пользователь сохранен как: {nickname}")
        send_to_all(f"Пользователь {nickname} присоединился к чату".encode('utf-8'), sender_socket=client_socket)
    
        while True:
            raw_message = client_socket.recv(1024)
            if not raw_message:
                break
            
            message = raw_message.decode('utf-8')
            user_message = f"{nickname}: {message}".encode('utf-8')
            send_to_all(user_message, sender_socket=client_socket)
    except Exception as e:
        print(f"Ошибка с клиентом {e}")

    finally:
        if client_socket in clients:
            index = clients.index(client_socket)
            clients.remove(client_socket)
            client_socket.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)

            exit_massage = f"Пользователь {nickname} покинул чат".encode('utf-8')
            print(exit_massage.decode('utf-8'))
            send_to_all(exit_massage)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # для мгновенного освобождения порта сервера
    server.bind((HOST, PORT))
    server.listen()
    print("Сервер запущен и ждет подключений")

    while True:
        client_socket, client_address = server.accept()
        print(f"Новое соединение с адресом: {str(client_address)}")

        thread = threading.Thread(target=for_one_client, args = (client_socket,))
        thread.start()


if __name__ == "__main__":
    start_server()
