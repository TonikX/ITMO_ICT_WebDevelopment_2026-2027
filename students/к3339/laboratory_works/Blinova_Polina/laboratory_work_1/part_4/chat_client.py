import socket
import threading
import json
import sys


class ChatClient:
    def __init__(self, host='localhost', port=12347):
        self.host = host
        self.port = port
        self.socket = None
        self.username = None
        self.running = True

    def connect(self, username):
        self.username = username
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))

            self.socket.send(json.dumps({'username': username}).encode('utf-8'))

            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True
            thread.start()

            print(f"Подключен как {username}")
            print("Команды:")
            print(" /users - список пользователей в чате")
            print(" /pm <имя> <сообщение> - личное сообщение")
            print(" /quit - выход из чата")
            print("-" * 50)
            return True

        except ConnectionRefusedError:
            print("Ошибка: сервер не запущен")
            return False
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def receive_messages(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break

                message = json.loads(data.decode('utf-8'))
                self.display_message(message)

            except json.JSONDecodeError:
                continue
            except Exception:
                break

        if self.running:
            print("\nСоединение с сервером потеряно")
            self.running = False

    def display_message(self, message):
        msg_type = message.get('type')

        if msg_type == 'system':
            print(f"\n[система] {message['message']}")
        elif msg_type == 'message':
            print(f"\n[{message['timestamp']}] {message['username']}: {message['message']}")
        elif msg_type == 'private':
            print(f"\n[лс] [{message['timestamp']}] {message['username']}: {message['message']}")
        elif msg_type == 'error':
            print(f"\n[ошибка] {message['message']}")
        elif msg_type == 'users_list':
            users = message['users']
            print(f"\nПользователи в чате ({len(users)}):")
            for user in users:
                marker = " (это вы)" if user == self.username else ""
                print(f"{user}{marker}")

        print("> ", end='', flush=True)

    def send_message(self, text):
        if not text.strip():
            return True

        if text.startswith('/'):
            parts = text.split(' ', 2)
            cmd = parts[0].lower()

            if cmd == '/quit':
                self.running = False
                self.socket.close()
                return False

            elif cmd == '/users':
                self.socket.send(json.dumps({'type': 'users'}).encode('utf-8'))
                return True

            elif cmd == '/pm':
                if len(parts) < 3:
                    print("Использование: /pm <имя> <сообщение>")
                    return True

                target = parts[1]
                pm_text = parts[2]

                if not target.strip():
                    print("Ошибка: имя получателя не может быть пустым")
                    return True

                if not pm_text.strip():
                    print("Ошибка: сообщение не может быть пустым")
                    return True

                self.socket.send(json.dumps({
                    'type': 'private',
                    'target': target,
                    'message': pm_text
                }).encode('utf-8'))
                return True

            else:
                print("Неизвестная команда. Доступные: /users, /pm, /quit")
                return True

        self.socket.send(json.dumps({
            'type': 'message',
            'message': text
        }).encode('utf-8'))
        return True

    def run(self):
        while self.running:
            try:
                msg = input("> ")
                if not self.send_message(msg):
                    break
            except KeyboardInterrupt:
                print("\nВыход из чата...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
                break


if __name__ == "__main__":
    username = input("Введите имя пользователя: ").strip()

    if not username:
        print("Имя не может быть пустым")
        sys.exit(1)

    client = ChatClient()
    if client.connect(username):
        client.run()

    print("Чат завершен")