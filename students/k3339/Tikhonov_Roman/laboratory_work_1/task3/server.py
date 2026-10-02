import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8083))
sock.listen(1)
print("Сервер запущен. Откройте: http://127.0.0.1:8083")

conn, addr = sock.accept()
print("Подключился клиент:", addr)

data = conn.recv(1024)
print(data.decode())


f = open("index.html", encoding="utf-8")
body = f.read()
f.close()
body_bytes = body.encode("utf-8")

response = "HTTP/1.1 200 OK\r\n"
response += "Content-Type: text/html; charset=utf-8\r\n"
response += "Content-Length: " + str(len(body_bytes)) + "\r\n"
response += "\r\n"
response += body

conn.send(response.encode("utf-8"))
conn.close()
sock.close()