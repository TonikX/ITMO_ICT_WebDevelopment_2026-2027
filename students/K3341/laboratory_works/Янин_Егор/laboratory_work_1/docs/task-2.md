# Практическое задание 2. Вычисления через TCP

## Задание

Реализовать клиентскую и серверную часть приложения. Клиент запрашивает выполнение математической операции, параметры которой вводятся с клавиатуры. Сервер обрабатывает данные и возвращает результат клиенту.

Вариант 1: Теорема Пифагора

## Выполнение

```py
import socket
import math

def pifagor(a, b):
    return math.sqrt(a ** 2 + b ** 2)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 9090))
sock.listen(1)
print('Server is listening on port 9090...')

while True:
    conn, addr = sock.accept()
    print(f'Connection from {addr}')
    data = conn.recv(1024)
    a, b = map(int, data.decode('utf-8').split())
    result = pifagor(a, b)
    conn.sendall(str(result).encode('utf-8'))
    conn.close()
```

Сервер слушает на порте 9090, принимает на вход 2 числа - катеты прямоугольного треугольника, и возвращает число - гипотенузу этого треугольника, после чего закрывает соединение и повторяет сначала.

```py
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9090))
a = int(input('Enter the first number: '))
b = int(input('Enter the second number: '))
sock.sendall(f'{a} {b}'.encode('utf-8'))
data = sock.recv(1024)
print(f'The result is: {data.decode("utf-8")}')
sock.close()
```

Клиент подключается к серверу, принимает из консоли 2 числа и отправляет их, получает от сервера ответ и выводит его. после чего программа завершается.
