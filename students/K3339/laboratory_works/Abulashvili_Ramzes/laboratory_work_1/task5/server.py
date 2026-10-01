import json
import socket
from html import escape
from pathlib import Path
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8081
DATA_FILE = Path(__file__).with_name("grades.json")


def make_page(grades, message=""):
    rows = "".join(
        f"<tr><td>{escape(subject)}</td><td>{', '.join(map(str, marks))}</td></tr>"
        for subject, marks in grades.items()
    )
    if not rows:
        rows = '<tr><td colspan="2">Оценок пока нет.</td></tr>'
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <p>{escape(message)}</p>
    <form method="post" action="/">
        <p><label>Предмет: <input name="subject" required></label></p>
        <p><label>Оценка: <input name="grade" type="number" min="2" max="5" required></label></p>
        <button type="submit">Добавить оценку</button>
    </form>
    <h2>Оценки по предметам</h2>
    <table border="1" cellpadding="6">
        <tr><th>Предмет</th><th>Оценки</th></tr>
        {rows}
    </table>
    <p><a href="/">Обновить журнал</a></p>
</body>
</html>"""


def send_response(connection, status, page, extra_headers=None):
    body = page.encode("utf-8")
    headers = [
        f"HTTP/1.1 {status}",
        "Content-Type: text/html; charset=utf-8",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    for name, value in (extra_headers or {}).items():
        headers.append(f"{name}: {value}")
    response = "\r\n".join(headers) + "\r\n\r\n"
    connection.sendall(response.encode("ascii") + body)


def read_request(connection):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = connection.recv(4096)
        if not chunk:
            raise ValueError("Запрос не получен полностью.")
        data += chunk
    header_data, body = data.split(b"\r\n\r\n", 1)
    lines = header_data.decode("iso-8859-1").split("\r\n")
    method, path, version = lines[0].split()
    headers = {}
    for line in lines[1:]:
        name, value = line.split(":", 1)
        headers[name.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length < 0:
        raise ValueError("Неверная длина тела запроса.")
    while len(body) < length:
        chunk = connection.recv(min(4096, length - len(body)))
        if not chunk:
            raise ValueError("Тело запроса не получено полностью.")
        body += chunk
    return method, body[:length]


def handle_request(connection, grades):
    method, body = read_request(connection)
    if method == "GET":
        send_response(connection, "200 OK", make_page(grades))
        return
    if method != "POST":
        send_response(connection, "405 Method Not Allowed", make_page(grades, "Метод не поддерживается."), {"Allow": "GET, POST"})
        return
    form = parse_qs(body.decode("utf-8"))
    subject = form.get("subject", [""])[0].strip()
    mark = form.get("grade", [""])[0].strip()
    if not subject or mark not in ("2", "3", "4", "5"):
        send_response(connection, "400 Bad Request", make_page(grades, "Укажите предмет и целую оценку от 2 до 5."))
        return
    updated = {**grades, subject: grades.get(subject, []) + [int(mark)]}
    DATA_FILE.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
    grades.update(updated)
    send_response(connection, "303 See Other", make_page(grades, "Оценка сохранена."), {"Location": "/"})


def main():
    grades = {}
    if DATA_FILE.exists():
        grades = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Журнал оценок: http://{HOST}:{PORT}/. Остановка: Ctrl+C.")
        while True:
            connection, address = server.accept()
            with connection:
                connection.settimeout(5)
                try:
                    handle_request(connection, grades)
                except (ValueError, OSError) as error:
                    print(f"Не удалось обработать запрос от {address}: {error}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    except (OSError, ValueError) as error:
        print(f"Не удалось запустить сервер: {error}")
