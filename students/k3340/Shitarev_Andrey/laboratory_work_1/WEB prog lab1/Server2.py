import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('', 9090))

print("Server up")

sock.listen(1)
client_sock, client_address = sock.accept()
print(f"Соединение с устройством с адресом {client_address} установлено")

while True:
    client_data = client_sock.recv(1024)
    if not client_data:
        break
    recived_data = client_data.decode('utf-8')
    print(f"Данные полученные от клиента: {recived_data}")

    try:
        parts = recived_data.split()
        if len(parts) == 2:
            osnovanie = float(parts[0])
            vysota = float(parts[1])

            S = osnovanie*vysota

            client_sock.sendall((f"Площадь параллелограмма равна: {S}").encode('utf-8'))
        else:
            client_sock.sendall(("Должно быть введено 2 числа через проблем").encode('utf-8'))
    except:
        client_sock.sendall((f"Неверный формат следующих данных: {recived_data}").encode('utf-8'))

client_sock.close()
sock.close()
input()

