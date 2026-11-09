import socket

# 1. Создаем сокет
# AF_INET = "Используем IPv4" (улица/дом)
# SOCK_DGRAM = "Datagram" (Открытка / UDP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. Привязываем сокет к адресу и порту (Занимаем номер кабинета)
# '' означает слушать все доступные сетевые интерфейсы
server_socket.bind(('', 12345))
print("UDP Сервер запущен и ждет открыток...")

# 3. Принимаем данные
# recvfrom замирает, пока кто-то не пришлет данные.
# Возвращает кортеж: (сами_данные, адрес_отправителя)
# 1024 — максимальный размер пакета в байтах (размер конверта)
data, client_address = server_socket.recvfrom(1024)

# Сетевые данные передаются в байтах, поэтому делаем .decode() в строку
print(f"Получено от {client_address}: {data.decode('utf-8')}")

# 4. Отправляем ответ
response = "Привет от UDP сервера!".encode('utf-8')
server_socket.sendto(response, client_address)

# 5. Закрываем сокет (вешаем трубку)
server_socket.close()