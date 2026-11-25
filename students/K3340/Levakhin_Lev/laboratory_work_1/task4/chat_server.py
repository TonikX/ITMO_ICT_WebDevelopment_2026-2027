"""
- Многопользовательский TCP-чат
Сервер держит по одному потоку на каждого клиента и рассылает
входящие сообщения всем остальным участникам
"""

import socket
import threading

HOST = '127.0.0.1'
PORT = 9093

class ChatServer:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        # Словарь: сокет клиента -> его имя
        # Сокет используем как ключ потому что он уникален для каждого соединения
        self.clients: dict[socket.socket, str] = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f"[Сервер] Слушает {self.host}:{self.port}")

        try:
            while True:
                conn, addr = server_socket.accept()
                # Для каждого клиента свой поток
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True, # Чтобы поток завершился вместе с программой при Ctrl+C
                )
                thread.start()
        except KeyboardInterrupt:
            print("\n[Сервер] Остановлен")
        finally:
            server_socket.close()

    def handle_client(self, conn: socket.socket, addr: tuple) -> None:
        """Авторизация, чтение сообщений, выход"""
        name = None
        try:
            # Для авторизации исполдьзуем имя
            name = self._receive_line(conn).strip()
            if not name:
                conn.close()
                return

            self._register(conn, name, addr)
            self._broadcast(f"[СИСТЕМА] {name} присоединился к чату", exclude=conn)

            # Читаем сообщения пока клиент не выйдет
            while True:
                message = self._receive_line(conn)
                if not message:
                    break
                if message.strip().lower() in ('!exit', '/exit'):
                    break
                self._broadcast(f"{name}: {message}", exclude=conn)

        except (ConnectionResetError, OSError):
            # Клиент мог аварийно отвалиться — не считаем это ошибкой сервера.
            pass
        finally:
            self._unregister(conn, name)
            if name:
                self._broadcast(f"[СИСТЕМА] {name} покинул чат")
            conn.close()

    def _receive_line(self, conn: socket.socket) -> str:
        """Читает одну строку (до \\n) из сокета"""
        data = conn.recv(1024)
        return data.decode('utf-8').rstrip('\r\n') if data else ''

    def _register(self, conn: socket.socket, name: str, addr: tuple) -> None:
        with self.lock:
            self.clients[conn] = name
        print(f"[Сервер] {name} подключился ({addr[0]}:{addr[1]}). Всего: {len(self.clients)}")

    def _unregister(self, conn: socket.socket, name: str | None) -> None:
        with self.lock:
            self.clients.pop(conn, None)
        if name:
            print(f"[Сервер] {name} отключился. Осталось: {len(self.clients)}")

    def _broadcast(self, message: str, exclude: socket.socket | None = None) -> None:
        """Рассылает сообщение всем клиентам, кроме отправителя"""
        payload = (message + '\n').encode('utf-8')

        # Копируем список клиентов под замком, чтобы не держать его
        with self.lock:
            recipients = list(self.clients.keys())

        for client in recipients:
            if client is exclude:
                continue
            try:
                client.sendall(payload)
            except OSError:
                # Если клиенту не удалось отправить — отключаем его
                self._unregister(client, self.clients.get(client))


if __name__ == '__main__':
    ChatServer(HOST, PORT).start()