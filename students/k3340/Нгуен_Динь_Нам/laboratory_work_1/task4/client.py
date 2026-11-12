import socket
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('localhost', 8080))

def receive_messages():
    buffer = b""
    while True:
        try:
            response = client_socket.recv(1024)
        except OSError:
            break
        if not response:
            break
        buffer += response

        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            print(line.decode("utf-8"))
        
def send_messages():
    while True:
        message = input()
        if message.lower() == 'exit':
            break
        client_socket.sendall((message + "\n").encode('utf-8'))

nickname = input("Enter your nickname: ")

client_socket.sendall((nickname + "\n").encode('utf-8'))

thread = threading.Thread(target=receive_messages)
thread.start()

try:
    send_messages()
    
finally:
    try:
        client_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    client_socket.close()
    thread.join()
    


