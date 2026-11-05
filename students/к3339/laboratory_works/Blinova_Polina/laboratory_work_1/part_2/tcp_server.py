import socket
import json

def calculate_parallelogram_area(base, height):
    if base <= 0 or height <= 0:
        raise ValueError("Основание и высота должны быть положительными числами")
    return base * height

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            request = json.loads(data.decode('utf-8'))
            
            if request['operation'] == 'parallelogram_area':
                base = float(request['base'])
                height = float(request['height'])
                
                try:
                    area = calculate_parallelogram_area(base, height)
                    
                    response = {
                        'status': 'success',
                        'area': area
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))

                except ValueError as e:
                    response = {
                        'status': 'error',
                        'message': str(e)
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
            else:
                response = {
                    'status': 'error',
                    'message': 'Неизвестная операция'
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
                
    except Exception as e:
        print(f"Ошибка при обработке клиента: {e}")
    finally:
        client_socket.close()

def run_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 12346))
    server_socket.listen(5)
    
    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Подключен клиент: {address}")
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_tcp_server()