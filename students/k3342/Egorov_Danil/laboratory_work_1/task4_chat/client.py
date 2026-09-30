import socket
import threading

HOST, PORT = "localhost", 8080

stop = threading.Event()


def receive(reader):
    """Отдельный поток: печатает всё, что присылает сервер."""
    for line in reader:
        print(line.rstrip("\n"))
    print("Соединение с сервером закрыто. Нажмите Enter для выхода.")
    stop.set()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Не удалось подключиться: сервер не запущен.")
    raise SystemExit(1)

reader = client_socket.makefile("r", encoding="utf-8")
threading.Thread(target=receive, args=(reader,), daemon=True).start()

try:
    while not stop.is_set():
        text = input()
        if stop.is_set():
            break
        client_socket.sendall((text + "\n").encode("utf-8"))
        if text.strip() == "/exit":
            break
except (EOFError, KeyboardInterrupt):
    try:
        client_socket.sendall(b"/exit\n")
    except OSError:
        pass
finally:
    client_socket.close()
    print("Вы вышли из чата.")
