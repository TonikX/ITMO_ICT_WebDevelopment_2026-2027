import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 9095))
sock.listen(5) 

print("Сервер поднят и готов принять запрос")

while True:
    client_sock, client_address = sock.accept() # теперь сервер будет обслуживать ни 1 клиента на протяжении всей своей работы, а всех желающих
    request = client_sock.recv(1024)
    if not request:
        client_sock.close() # если браузер открыл подключение и ничего не прислал теперь просто ждем следующего подключения, а не закрываем сокет сервера
        continue

    print(f"Сервер получил запрос от {client_address}:\n{request.decode('utf-8')[:100]}... \n") # первые 100 символов запроса


    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            body = file.read()
    except FileNotFoundError:
        body = "<h1>Файл index.html не найден<h1>" # оборачиваем текст ошибки в тело HTTP ответа

    content_length = len(body.encode('utf-8'))

    response_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {content_length}\r\n"
        "Connection: close\r\n"
        "\r\n"
        )


    response = response_headers + body
    client_sock.sendall(response.encode('utf-8'))

    client_sock.close()