import socket
import threading


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002
ENCODING = "utf-8"


class ChatClient:
    def __init__(self) -> None:
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self._reader = None

    def run(self) -> None:
        username = input("Введите имя пользователя: ").strip()

        if not username:
            print("Имя пользователя не может быть пустым")
            return

        try:
            self._socket.connect((SERVER_HOST, SERVER_PORT))
            self._reader = self._socket.makefile(
                "r",
                encoding=ENCODING,
                newline="\n",
            )

            self._send(username)

            response = self._reader.readline().rstrip("\n")

            if response.startswith("ERROR "):
                print(response.removeprefix("ERROR "))
                return

            print(response.removeprefix("OK "))
            print("Введите сообщение.")
            print("Для выхода из чата введите /exit")

            receiver = threading.Thread(
                target=self._receive_messages,
                daemon=True,
            )
            receiver.start()

            while True:
                message = input()

                if not message:
                    continue

                self._send(message)

                if message == "/exit":
                    break

        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу")
        except (ConnectionResetError, BrokenPipeError):
            print("Соединение с сервером потеряно")
        finally:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            self._socket.close()

    def _receive_messages(self) -> None:
        if self._reader is None:
            return

        try:
            for line in self._reader:
                message = line.rstrip("\n")

                if message:
                    print(message)
        except OSError:
            pass

    def _send(self, message: str) -> None:
        self._socket.sendall(
            f"{message}\n".encode(ENCODING)
        )


if __name__ == "__main__":
    ChatClient().run()