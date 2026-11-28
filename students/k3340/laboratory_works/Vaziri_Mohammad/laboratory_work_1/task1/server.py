"""Задание 1. UDP-сервер: принимает «Hello, server» и отвечает «Hello, client»."""
import socket

HOST, PORT = "127.0.0.1", 9091


def main():
    # SOCK_DGRAM = UDP: соединение не устанавливается, работаем отдельными датаграммами
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        print(f"UDP-сервер слушает {HOST}:{PORT}")
        while True:
            data, addr = sock.recvfrom(1024)          # ждём датаграмму и адрес отправителя
            print(f"От {addr}: {data.decode('utf-8')}")
            sock.sendto("Hello, client".encode("utf-8"), addr)  # отвечаем на тот же адрес


if __name__ == "__main__":
    main()
