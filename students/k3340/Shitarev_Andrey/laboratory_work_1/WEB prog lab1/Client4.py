import socket
import threading
import sys
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(('127.0.0.1', 9080))
except ConnectionRefusedError:
    print("Не удалось соединиться с сервером")
    sys.exit()

authentificated = False

def recive_messages():
    global authentificated
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'Nickname_Request':
                nickname = input('Сервер запрашивает имя пользователя: ')
                client.send(nickname.encode('utf-8'))
                authentificated = True
                print("Вы успешно авторизовались, для выхода из чата введите esc")
           
            else:
                print(message)
        except:
            print("Соединение с сервером потеряно")
            client.close()
            break

def send_messages():
    while True:
        if not authentificated:
            time.sleep(0.1)
            continue

        raw_message = input("Введите текст: ")
        if raw_message.lower() == 'esc':
            client.close()
            sys.exit()

        try:
            client.sendall(raw_message.encode('utf-8'))
        except:
            break

threading.Thread(target=recive_messages, daemon = True).start() # фоновый процесс
threading.Thread(target=send_messages).start()



        

                 
