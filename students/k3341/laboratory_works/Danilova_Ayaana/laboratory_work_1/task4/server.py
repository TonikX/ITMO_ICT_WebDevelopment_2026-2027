import logging
import select
import socket
import threading

HOST, PORT = '127.0.0.1', 9002
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
clients = {str: socket.socket}

lock = threading.Lock()


def send_message(msg: str, sender_login: str = None):
    with lock:
        for client, sock in list(clients.items()):
            if client != sender_login:
                try:
                    sock.sendall(msg.encode("utf-8"))
                    logging.info(f"Успешно: {sender_login} отправил сообщение '{msg}' {client}")
                except Exception as e:
                    logging.error(f"Ошибка: не удалось оправить сообщение {sender_login} с содержимым: '{msg}'.\r\n{e}")


def handle_client(client_sock, client_address):
    login = None
    try:
        raw_login = client_sock.recv(1024).decode("utf-8").strip()
        if not raw_login or raw_login.isspace():
            client_sock.sendall("ERROR: Логин не был введен\n".encode("utf-8"))
            logging.warning(f"Отказ: {client_address} ввел пустой логин")
            # заканчивается обработка клиента, то есть в чат он не вошел бедни
            return

        with lock:
            if raw_login in clients:
                client_sock.sendall(f"ERROR: Логин '{raw_login}' уже занят\n".encode("utf-8"))
                logging.warning(f"Отказ: логин '{raw_login}' уже используется ({client_address})")
                return
            # уведомляем, что все ок и начинаем держать активным сокет с пользователем = присоединение к чату
            login = raw_login
            clients[login] = client_sock
            client_sock.sendall(f"OK: Вы присоединились к чату с логином {login}\n".encode("utf-8"))
        logging.info(f"Пользователь '{login}' подключился с {client_address}")
        send_message(f"SYSTEM: Пользователь {login} вошел в чат!")

        # беспрерывно получаем сообщение от пользователя и отправляем в чат
        while True:
            msg = client_sock.recv(1024).decode("utf-8")
            # на клиенте вызвали sock.close() или sys.exit()
            if not msg:
                break
            if msg.lower() == '/exit':
                break
            client_sock.sendall("OK: Сообщение отправлено".encode("utf-8"))
            logging.info(f"[{login}]: {msg}")
            send_message(f"[{login}]: {msg}", sender_login=login)
    finally:
        if login:
            with lock:
                if login in clients:
                    del clients[login]
            logging.info(f"Пользователь '{login}' вышел из чата.")
            send_message(f"SYSTEM: Пользователь {login} покинул чат.")

        client_sock.close()


def start_server(HOST: str, PORT: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)

    logging.info(f"ЧАТ-сервер запущен на {HOST}:{PORT}")

    try:
        while True:
            readable, _, _ = select.select([sock], [], [], 0.5)
            if sock in readable:
                client_sock, client_addr = sock.accept()

                thread = threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True)
                thread.start()
    except KeyboardInterrupt:
        print("\n[OK] Сервер успешно остановлен (Ctrl+C).")
    finally:
        sock.close()


if __name__ == "__main__":
    start_server(HOST, PORT)
