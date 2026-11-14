import socket
import threading
import os

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"\n{message}")
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9090))

name = input("Введите ваше имя: ")

thread = threading.Thread(target=receive_messages, args=(client,))
thread.start()

while True:
    msg = input()
    
    if msg.lower() == 'exit':
        client.close()
        os._exit(0)
        
    full_message = f"{name}: {msg}"
    client.send(full_message.encode('utf-8'))