import socket
from html import escape
from urllib.parse import unquote

ADDRESS = "127.0.0.1"
PORT = 9005

journal = {}


def read_form(body):
    fields = body.split("&")
    parsed = {}
    for part in fields:
        if "=" in part:
            key, value = part.split("=", 1)
            parsed[unquote(key)] = unquote(value)
    return parsed


def save_mark(body):
    data = read_form(body)
    subject = data.get("subject", "")
    score = data.get("grade", "")
    if not subject or not score:
        return "400 Bad Request", "Не указан предмет или оценка"

    if subject in journal:
        journal[subject].append(score)
    else:
        journal[subject] = [score]

    return "200 OK", f"Сохранено: {subject} = {score}"


def make_page():
    lines = []
    if not journal:
        lines.append("<p>Журнал пуст.</p>")
    else:
        lines.append("<ul>")
        for subject, scores in journal.items():
            safe = ", ".join(escape(s) for s in scores)
            lines.append(f"<li>{escape(subject)}: {safe}</li>")
        lines.append("</ul>")

    page = "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Журнал</title></head>"
    page += "<body><h1>Журнал оценок</h1>" + "".join(lines) + "</body></html>"
    return page


def respond(conn, request):
    lines = request.split("\r\n")
    head = lines[0].split()
    if len(head) < 2:
        conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        return

    method, path = head[0], head[1]
    body = ""
    if method == "POST":
        length = 0
        for line in lines[1:]:
            if line.lower().startswith("content-length:"):
                length = int(line.split(":", 1)[1].strip())
        if length:
            body = request.split("\r\n\r\n", 1)[1][:length]

    if method == "GET" and path in ("/", "/grades"):
        status = "200 OK"
        payload = make_page().encode("utf-8")
    elif method == "POST" and path == "/grade":
        status, text = save_mark(body)
        payload = text.encode("utf-8")
    else:
        status = "404 Not Found"
        payload = "Страница не найдена".encode("utf-8")

    header = f"HTTP/1.1 {status}\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(payload)}\r\nConnection: close\r\n\r\n"
    conn.sendall(header.encode("utf-8") + payload)


def process(conn, address):
    request = conn.recv(65536).decode("utf-8", errors="replace")
    if request:
        print(f"{address}: {request.splitlines()[0]}")
        respond(conn, request)
    conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ADDRESS, PORT))
    server.listen(5)
    print(f"Сервер на http://{ADDRESS}:{PORT}")

    while True:
        conn, address = server.accept()
        process(conn, address)


main()