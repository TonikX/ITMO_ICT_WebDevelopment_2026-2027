import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 12345))

hello = sock.recv(1024).decode("utf-8")
print(f"[Сервер] {hello}. Нажмите Ctrl+C для остановки.")

try:
    sock.sendall(f"{input()}\n".encode("utf-8"))
except KeyboardInterrupt:
    print("\n[OK] Клиент успешно остановлен пользователем (Ctrl+C).")
    sock.close()
    sys.exit(-1)

ans = sock.recv(1024).decode("utf-8")
print(f"Получен ответ от сервера, площадь трапеции = {ans}")

sock.close()
