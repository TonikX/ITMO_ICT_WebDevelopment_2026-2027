import select
import socket


def calc_trapezoid_area(a: float, b: float, h: float) -> float:
    if a <= 0 or b <= 0 or h <= 0:
        raise ValueError()
    return (a + b) / 2 * h


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 12345))
sock.listen(5)

print("Сервер запущен. Нажмите Ctrl+C для остановки...")

try:
    while True:
        readable, _, _ = select.select([sock], [], [], 0.5)
        if sock in readable:
            client_sock, client_addr = sock.accept()
            print(f"Подключился клиент: {client_addr}")

            try:
                client_sock.sendall("Введите основания и высоту в следующем порядке через пробел: a b h".encode("utf-8"))

                data = client_sock.recv(1024)
                if not data:
                    continue

                data = data.decode("utf-8", errors='ignore').rstrip()
                if not data:
                    client_sock.sendall("Получен пустой ввод. Сокет выключается.\n".encode("utf-8"))
                    break

                parts = data.split()
                if len(parts) != 3:
                    client_sock.sendall("Надо ввести ровно 3 переменные через пробел".encode("utf-8"))
                    continue

                a, b, h = map(float, parts)
                print(f"Полученные значения: a={a}, b={b}, h={h}")
                client_sock.sendall(f"{calc_trapezoid_area(a, b, h)}".encode("utf-8"))

            except ValueError:
                client_sock.sendall("Ошибка: введенные данные должны быть позитивными числами!\n".encode("utf-8"))
            except Exception as e:
                client_sock.sendall("Ошибка: что-то со связью\n".encode("utf-8"))
            finally:
                client_sock.close()

except KeyboardInterrupt:
    print("\n[OK] Сервер успешно остановлен (Ctrl+C).")
finally:
    sock.close()