import socket
import sys
import threading

from server import HOST, PORT

lock = threading.Lock()


def receive_messages(sock: socket.socket):
    while True:
        try:
            msg = sock.recv(1024).decode("utf-8")
            # срабатывает при client_sock.close()
            if not msg:
                print("\n[Сервер]: Соединение разорвано.")
                break
            print(f"\n{msg}\nВаше сообщение > ", end="")
        except Exception:
            break
    sock.close()


def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
    except Exception as e:
        print(f"Не удалось подключиться к серверу: {e}")
        return
    login = input("Ваш логин > ").strip()
    if not login:
        print("ERROR: Логин не был введен")
        return
    try:
        sock.sendall(login.encode("utf-8"))
    except Exception as e:
        print(f"Не удалось отправить логин серверу: {e}")
        return

    recv_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    recv_thread.start()

    print("Подключение успешно! Наберите '/exit' для выхода из чата.")

    while True:
        try:
            msg = input("Ваше сообщение > ")
            if not msg:
                continue
            if msg.lower() == "/exit":
                print("Выходим из чата")
                break
            sock.sendall(msg.encode("utf-8"))

        except (OSError, ConnectionResetError, BrokenPipeError):
            # сокет уже закрыт потоком чтения, ничего отправлять не нужно
            print("\n[Клиент]: Отправка невозможна, соединение потеряно.")
            break
        except KeyboardInterrupt:
            # отправляем /exit только если сокет еще успешен
            try:
                sock.sendall("/exit".encode("utf-8"))
            except OSError:
                pass
            break
    sock.close()
    sys.exit()


if __name__ == "__main__":
    start_client()
