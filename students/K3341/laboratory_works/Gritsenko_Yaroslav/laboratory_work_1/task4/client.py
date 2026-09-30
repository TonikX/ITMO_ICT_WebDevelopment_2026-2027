import socket
import threading

from laboratory_work_1.common.cli import network_parser


def receive_loop(stream, stopped):
    try:
        for line in stream:
            print("\n" + line.rstrip("\n"))
    except OSError:
        pass
    finally:
        stopped.set()
        print("\nСоединение закрыто. Если ожидается ввод, нажмите Enter.")


def run(host, port, name):
    if not name.strip():
        raise ValueError("Введите имя")
    stopped = threading.Event()
    with socket.create_connection((host, port), timeout=5) as client:
        client.sendall((name + "\n").encode("utf-8"))
        with client.makefile("r", encoding="utf-8") as stream:
            welcome = stream.readline()
            if not welcome:
                raise ValueError("Сервер закрыл соединение")
            print(welcome.strip())
            client.settimeout(None)
            receiver = threading.Thread(target=receive_loop, args=(stream, stopped), daemon=True)
            receiver.start()
            try:
                while not stopped.is_set():
                    text = input("> ")
                    if stopped.is_set():
                        break
                    client.sendall((text + "\n").encode("utf-8"))
                    if text == "/quit":
                        break
            except (EOFError, KeyboardInterrupt):
                pass
            finally:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                receiver.join(timeout=2)


if __name__ == "__main__":
    parser = network_parser(9004)
    parser.add_argument("--name", help="Имя в чате; если не задано, вводится с клавиатуры")
    args = parser.parse_args()
    try:
        run(args.host, args.port, args.name or input("Ваше имя: "))
    except (ValueError, OSError, EOFError, KeyboardInterrupt) as error:
        raise SystemExit(f"Ошибка: {error}")
