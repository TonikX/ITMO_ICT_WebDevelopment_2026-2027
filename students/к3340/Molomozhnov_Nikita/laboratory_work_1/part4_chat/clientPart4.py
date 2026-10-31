import socket
import threading

def receive(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode('utf-8', errors='replace'), end='')
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5013))
threading.Thread(target=receive, args=(client,), daemon=True).start()

while True:
    try:
        msg = input()
        if not msg.strip():
            continue
        client.send(msg.encode('utf-8', errors='ignore'))
        if msg.strip() == '/quit':
            break
    except (KeyboardInterrupt, EOFError):
        print("\n[СИСТЕМА] Выход...")
        break

client.close()