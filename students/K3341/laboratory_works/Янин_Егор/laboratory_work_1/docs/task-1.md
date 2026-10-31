# Практическое задание 1. Обмен сообщениями по UDP

## Задание

Реализовать клиентскую и серверную часть приложения. Клиент отправляет серверу сообщение «Hello, server», и оно должно отобразиться на стороне сервера. В ответ сервер отправляет клиенту сообщение «Hello, client», которое должно отобразиться у клиента.

## Выполнение

```py
import socket

PORT = 9090

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))
print(f'Server is listening on port {PORT}...')
data = sock.recvfrom(1024)
print(f'Message from client: {data[0].decode('utf-8')}')
sock.sendto(b'Hello, client', data[1])
```

Сервер ожидает сообщения на порте 9090, декодирует его, выводит и отправляет сообщение "Hello, client" на тот же адрес, после чего отключается.

```py
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b'Hello, server', ('localhost', 9090))
data = sock.recvfrom(1024)
print(f'Message from server: {data[0].decode('utf-8')}')
```

Клиент отправляет на сервер сообщение "Hello, server" и выодит ответ от сервера, после чего отключается.
