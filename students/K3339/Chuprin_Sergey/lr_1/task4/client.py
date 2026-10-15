import socket
import threading
from colorama import init, Fore, Style
init()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(('localhost', 40_000))

def get_answers():
    while True:
        try:
            answer = client.recv(1024)
            if not answer:
                break
            print(Fore.RED + answer.decode('utf-8') + Style.RESET_ALL)
        except:
            break

t = threading.Thread(target=get_answers)
t.start()

while True:
    message = input('')
    if message == '[выход]':
        client.close()
        break
    client.send(message.encode('utf-8'))

