import socket
import threading
import json
from datetime import datetime


class ChatServer:
    def __init__(self, host='localhost', port=12347):
        self.host = host
        self.port = port
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)

        print(f"Чат-сервер запущен на {self.host}:{self.port}")

        try:
            while True:
                client_socket, address = server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
        finally:
            server_socket.close()

    def handle_client(self, client_socket, address):
        username = None
        try:
            data = client_socket.recv(1024)
            if not data:
                return

            auth_data = json.loads(data.decode('utf-8'))
            username = auth_data.get('username')

            if not username or not username.strip():
                error = json.dumps({
                    'type': 'error',
                    'message': 'Имя пользователя не может быть пустым'
                })
                client_socket.send(error.encode('utf-8'))
                client_socket.close()
                return

            with self.lock:
                if username in self.clients:
                    error = json.dumps({
                        'type': 'error',
                        'message': 'Имя пользователя уже занято'
                    })
                    client_socket.send(error.encode('utf-8'))
                    client_socket.close()
                    return
                self.clients[username] = client_socket

            self.broadcast({
                'type': 'system',
                'message': f'Пользователь {username} присоединился к чату'
            }, exclude=username)
            print(f"{username} подключен")

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = json.loads(data.decode('utf-8'))

                if message['type'] == 'message':
                    self.handle_public_message(username, message)

                elif message['type'] == 'private':
                    self.handle_private_message(username, message, client_socket)

                elif message['type'] == 'users':
                    self.handle_users_request(username, client_socket)

        except json.JSONDecodeError:
            print(f"Ошибка: некорректный JSON от {username or address}")
        except Exception as e:
            print(f"Ошибка при обработке {username or address}: {e}")
        finally:
            if username:
                with self.lock:
                    if username in self.clients:
                        del self.clients[username]

                self.broadcast({
                    'type': 'system',
                    'message': f'Пользователь {username} покинул чат'
                })
                print(f"{username} отключен")

            client_socket.close()

    def handle_public_message(self, username, message):
        chat_msg = {
            'type': 'message',
            'username': username,
            'message': message['message'],
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.broadcast(chat_msg, exclude=username)

    def handle_private_message(self, username, message, client_socket):
        target = message.get('target', '').strip()

        if not target:
            self.send_error(client_socket, "Имя получателя не может быть пустым")
            return

        if target == username:
            self.send_error(client_socket, "Нельзя отправить личное сообщение самому себе")
            return

        private_msg = {
            'type': 'private',
            'username': username,
            'message': message['message'],
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }

        if self.send_private(target, private_msg):
            confirm = {
                'type': 'system',
                'message': f"Личное сообщение отправлено пользователю '{target}'"
            }
            client_socket.send(json.dumps(confirm).encode('utf-8'))
        else:
            with self.lock:
                available = [u for u in self.clients.keys() if u != username]

            if available:
                error_text = (f"Пользователь '{target}' не найден. "
                              f"Доступные пользователи: {', '.join(available)}")
            else:
                error_text = f"Пользователь '{target}' не найден. В чате больше никого нет"

            self.send_error(client_socket, error_text)

    def handle_users_request(self, username, client_socket):
        with self.lock:
            users = list(self.clients.keys())

        response = {
            'type': 'users_list',
            'users': users
        }
        client_socket.send(json.dumps(response).encode('utf-8'))

    def send_error(self, client_socket, error_text):
        error = {
            'type': 'error',
            'message': error_text
        }
        try:
            client_socket.send(json.dumps(error).encode('utf-8'))
        except Exception as e:
            print(f"Не удалось отправить ошибку: {e}")

    def broadcast(self, message, exclude=None):
        with self.lock:
            for username, client_socket in self.clients.items():
                if username != exclude:
                    try:
                        client_socket.send(json.dumps(message).encode('utf-8'))
                    except Exception as e:
                        print(f"Ошибка рассылки для {username}: {e}")

    def send_private(self, target, message):
        with self.lock:
            if target not in self.clients:
                print(f"{message['username']} -> {target}: пользователь не найден")
                return False

            try:
                self.clients[target].send(json.dumps(message).encode('utf-8'))
                print(f"Личное: {message['username']} -> {target}: {message['message']}")
                return True
            except Exception as e:
                print(f"Ошибка отправки для {target}: {e}")
                del self.clients[target]
                return False


if __name__ == "__main__":
    server = ChatServer()
    server.start()