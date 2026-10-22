import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 40_000))
server.listen()

all_clients = dict()
lock = threading.Lock()


def clean_connection(client, address):
    with lock:
        all_clients.pop(address)
    client.close()
    print(f'{address} отключился')

def chat_worker(client, address):
    try:
        while True:
            message = client.recv(1024)
            if not message:
                clean_connection(client, address)
                break
            else:
                with lock:
                    for addr in all_clients:
                        if addr != address:
                            text = f'{address}: {message.decode("utf-8")}'
                            all_clients[addr].send(text.encode("utf-8"))
                    print(f'{address}: {message.decode("utf-8")}')
    except:
        clean_connection(client, address)

while True:
    client, address = server.accept()
    print(f'{address} подключился')
    with lock:
        all_clients[address] = client

    t = threading.Thread(target=chat_worker, args=(client, address))
    t.start()


