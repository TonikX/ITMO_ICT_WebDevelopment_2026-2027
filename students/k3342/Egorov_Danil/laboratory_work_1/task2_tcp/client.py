import socket

HOST, PORT = "localhost", 8080


def read_number(prompt):
    """Запрашивает число с клавиатуры, пока не будет введено корректное."""
    while True:
        text = input(prompt).strip().replace(",", ".")
        try:
            float(text)
            return text
        except ValueError:
            print("Нужно ввести число, повторите.")


print("Теорема Пифагора")
a = read_number("Введите катет a: ")
b = read_number("Введите катет b: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.sendall(f"{a} {b}".encode("utf-8"))
print("Ответ сервера:", client_socket.recv(1024).decode("utf-8"))
client_socket.close()
