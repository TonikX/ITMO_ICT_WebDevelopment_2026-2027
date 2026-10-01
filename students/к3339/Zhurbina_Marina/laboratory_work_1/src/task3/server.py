import socket

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(("127.0.0.1", 9003))
listener.listen(1)
print("Сервер активен. Откройте: http://127.0.0.1:9003")

conn, addr = listener.accept()
print("Клиент:", addr)


with open("index.html", encoding="utf-8") as f:
    html = f.read()
html_bytes = html.encode("utf-8")

answer = "HTTP/1.1 200 OK\r\n"
answer += "Content-Type: text/html; charset=utf-8\r\n"
answer += "Content-Length: " + str(len(html_bytes)) + "\r\n"
answer += "\r\n"
answer += html

conn.send(answer.encode("utf-8"))
conn.close()
listener.close()