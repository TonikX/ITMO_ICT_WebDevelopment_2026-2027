import socket
import threading

from laboratory_work_1.common.cli import network_parser

clients = {}
lock = threading.Lock()


def broadcast(text, exclude=None):
    with lock:
        for connection in clients:
            if connection is not exclude:
                try:
                    connection.sendall((text + "\n").encode("utf-8"))
                except OSError:
                    pass


def handle(connection):
    with connection, connection.makefile("r", encoding="utf-8") as stream:
        name = stream.readline().strip()
        if not name:
            return
        with lock:
            connection.sendall(f"Вы вошли как {name}. Выход: /quit\n".encode("utf-8"))
            clients[connection] = name
        broadcast(f"{name} вошёл в чат", exclude=connection)
        try:
            for line in stream:
                text = line.rstrip("\n")
                if text == "/quit":
                    break
                if text.strip():
                    broadcast(f"{name}: {text}", exclude=connection)
        except OSError:
            pass
        finally:
            with lock:
                clients.pop(connection)
            broadcast(f"{name} вышел из чата")


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"TCP-чат: {host}:{server.getsockname()[1]}")
        while True:
            connection, _ = server.accept()
            threading.Thread(target=handle, args=(connection,), daemon=True).start()


if __name__ == "__main__":
    args = network_parser(9004).parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
