import socket
import threading


HOST = '127.0.0.1'
PORT = 9093
EXIT_COMMAND = '!exit'


class ChatClient:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def start(self) -> None:
        """Подключается, регистрируется и запускает параллельный приём сообщений"""
        self.socket.connect((self.host, self.port))

        name = input("Введите ваше имя: ").strip() or "Аноним"
        self._send(name)   # первое сообщение — имя

        receiver = threading.Thread(target=self._receive_loop, daemon=True)
        receiver.start()

        self._send_loop()

    def _send_loop(self) -> None:
        """Читает строки из stdin и отправляет их серверу"""
        try:
            while self.running:
                text = input()
                if text.strip().lower() == EXIT_COMMAND:
                    self._send(EXIT_COMMAND)
                    break
                self._send(text)
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            self._shutdown()

    def _send(self, text: str) -> None:
        """Отправляет одну строку, добавляя \\n как разделитель"""
        try:
            self.socket.sendall((text + '\n').encode('utf-8'))
        except OSError:
            self.running = False

    def _receive_loop(self) -> None:
        """Принимает сообщения от сервера и печатает их"""
        while self.running:
            try:
                data = self.socket.recv(1024)
            except OSError:
                break
            if not data:
                print("\n[Клиент] Соединение закрыто сервером.")
                break
            # Может прийти несколько строк сразу — печатаем каждую.
            for line in data.decode('utf-8').splitlines():
                print(f"\r{line}\n> ", end='', flush=True)

        self.running = False

    def _shutdown(self) -> None:
        self.running = False
        try:
            self.socket.close()
        except OSError:
            pass
        print("[Клиент] Покинул(а) чат")


if __name__ == '__main__':
    ChatClient(HOST, PORT).start()