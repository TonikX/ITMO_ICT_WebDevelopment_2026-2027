import socket
import os

def make_new_socket():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 45_001))
    return client

def get_marks():
    client = make_new_socket()
    get_request_template = \
        (
        "GET / HTTP/1.1\r\n"
        "Host: localhost\r\n\r\n"
        )
    client.send(get_request_template.encode('utf-8'))
    response = client.recv(4096)
    print(response.decode('utf-8'))
    client.close()

def add_mark():
    client = make_new_socket()
    subject = input('Введите предмет: ')
    mark = input('Введите оценку (1-5): ').strip()
    if mark not in ['1', '2', '3', '4', '5']:
        return
    body = f"{subject} : {mark}"
    post_request_template = \
        (
        "POST / HTTP/1.1\r\n"
        "Host: localhost\r\n"
        f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n"
        f"{body}"
    )
    print('send')
    client.send(post_request_template.encode('utf-8'))
    response = client.recv(4096)
    print(response.decode('utf-8'))
    client.close()

while True:
    os.system('clear')
    print('Журнал оценок')
    print('1. Просмотреть все оценки')
    print('2. Добавить новую оценку')
    print('0. Выход')
    inp = input('Введите цифру -> ')
    if inp == '0':
        break
    if inp == '1':
        get_marks()
        input()
    if inp == '2':
        add_mark()
        input()
