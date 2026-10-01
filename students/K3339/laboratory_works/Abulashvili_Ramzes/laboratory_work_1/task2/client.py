import socket

HOST = "127.0.0.1"
PORT = 5002


def main():
    try:
        a = float(input("Первый катет: ").replace(",", "."))
        b = float(input("Второй катет: ").replace(",", "."))
    except ValueError:
        print("Введите два числа.")
        return
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as client:
            client.sendall(f"{a} {b}\n".encode("utf-8"))
            with client.makefile("rb") as reader:
                data = reader.readline()
            if not data:
                print("Сервер закрыл соединение без ответа.")
                return
            print(data.decode("utf-8").strip())
    except OSError as error:
        print(f"Не удалось получить ответ сервера: {error}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nКлиент остановлен.")
