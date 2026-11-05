import socket
import json

def run_tcp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect(('localhost', 12346))
        
        while True:
            print("\nВведите данные для вычисления площади параллелограмма:")
            try:
                base = float(input("Введите длину основания: "))
                height = float(input("Введите высоту: "))
                
                if base <= 0 or height <= 0:
                    print("Ошибка: основание и высота должны быть положительными числами")
                    continue
                    
            except ValueError:
                print("Ошибка: введите числа")
                continue
            
            request = {
                'operation': 'parallelogram_area',
                'base': base,
                'height': height
            }
            
            client_socket.send(json.dumps(request).encode('utf-8'))
            
            response_data = client_socket.recv(1024)
            response = json.loads(response_data.decode('utf-8'))
            
            if response['status'] == 'success':
                print(f"\nРезультат:")
                print(f"Площадь параллелограмма: {response['area']:.2f}")
            else:
                print(f"Ошибка: {response['message']}")
            
            cont = input("\nПродолжить? (y/n): ")
            if cont.lower() != 'y':
                break
                
    except ConnectionRefusedError:
        print("Ошибка: Сервер не запущен")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    run_tcp_client()