"""Задание 3."""
import socket

HOST = "127.0.0.1"
PORT = 8080

def main():
    request = "GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            client.sendall(request.encode("ascii"))
            chunks = []
            while True:
                data = client.recv(4096)
                if not data:
                    break
                chunks.append(data)
        response = b"".join(chunks).decode("utf-8", errors="replace")
        print("Получен HTTP-ответ:\n")
        print(response)
    except ConnectionRefusedError:
        print("Не удалось подключиться. Сначала запустите server.py.")

if __name__ == "__main__":
    main()
