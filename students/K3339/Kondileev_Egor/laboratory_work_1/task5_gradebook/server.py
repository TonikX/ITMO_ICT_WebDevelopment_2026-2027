"""Практическое задание 5: HTTP GET/POST сервер на socket."""
from html import escape
from urllib.parse import parse_qs
import json
import socket

HOST = "127.0.0.1"
PORT = 8085
MAX_BODY_SIZE = 100_000

gradebook = {}


def make_response(status, body, content_type="text/html; charset=utf-8"):
    if isinstance(body, str):
        body = body.encode("utf-8")
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("ascii")
    return headers + body


def read_request(connection):
    """Читает HTTP-заголовки и тело указанной в Content-Length длины."""
    data = bytearray()
    while b"\r\n\r\n" not in data:
        part = connection.recv(4096)
        if not part:
            return None
        data.extend(part)
        if len(data) > MAX_BODY_SIZE + 16384:
            raise ValueError("Слишком большой HTTP-запрос")

    header_bytes, body = bytes(data).split(b"\r\n\r\n", 1)
    lines = header_bytes.decode("iso-8859-1").split("\r\n")
    parts = lines[0].split()
    if len(parts) != 3:
        raise ValueError("Некорректная строка HTTP-запроса")

    method, path, _version = parts
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    try:
        length = int(headers.get("content-length", "0"))
    except ValueError:
        raise ValueError("Некорректный Content-Length")
    if length < 0 or length > MAX_BODY_SIZE:
        raise ValueError("Недопустимый размер тела запроса")

    while len(body) < length:
        part = connection.recv(min(4096, length - len(body)))
        if not part:
            raise ValueError("Запрос оборвался до получения тела")
        body += part

    return method, path.split("?", 1)[0], headers, body[:length]


def render_page(message=""):
    rows = []
    if not gradebook:
        rows.append('<tr><td colspan="2">Оценок пока нет.</td></tr>')
    else:
        for subject in sorted(gradebook, key=str.casefold):
            grades = ", ".join(map(str, gradebook[subject]))
            rows.append(f"<tr><td>{escape(subject)}</td><td>{escape(grades)}</td></tr>")

    notice = f"<p>{escape(message)}</p>" if message else ""
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Журнал оценок</title>
<style>
body {{ max-width: 800px; margin: 40px auto; padding: 0 16px; font: 16px Arial, sans-serif; }}
form {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: end; margin-bottom: 28px; }}
label {{ display: grid; gap: 6px; }}
input, button {{ padding: 9px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ border: 1px solid #aaa; padding: 10px; text-align: left; }}
th {{ background: #eee; }}
</style>
</head>
<body>
<h1>Журнал оценок</h1>
{notice}
<h2>Добавить оценку</h2>
<form method="post" action="/grades">
<label>Дисциплина
<input name="subject" required maxlength="100" placeholder="Например, Математика">
</label>
<label>Оценка (2–5)
<input name="grade" type="number" min="2" max="5" step="1" required>
</label>
<button type="submit">Сохранить</button>
</form>
<h2>Все оценки по дисциплинам</h2>
<table>
<thead><tr><th>Дисциплина</th><th>Оценки</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</body>
</html>"""


def parse_grade(body, headers):
    """Поддерживает HTML-форму браузера и JSON."""
    content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
    text = body.decode("utf-8")

    if content_type == "application/json":
        payload = json.loads(text)
        subject = str(payload.get("subject", "")).strip()
        grade_value = payload.get("grade")
    else:
        form = parse_qs(text, keep_blank_values=True)
        subject = form.get("subject", [""])[0].strip()
        grade_value = form.get("grade", [""])[0]

    if not subject:
        raise ValueError("Укажите название дисциплины.")
    if len(subject) > 100:
        raise ValueError("Название дисциплины должно быть не длиннее 100 символов.")
    if isinstance(grade_value, bool) or grade_value is None:
        raise ValueError("Оценка должна быть целым числом от 2 до 5.")
    grade_text = str(grade_value).strip()
    try:
        grade = int(grade_text)
    except (ValueError, TypeError):
        raise ValueError("Оценка должна быть целым числом от 2 до 5.")
    if not isinstance(grade_value, int) and str(grade) != grade_text:
        raise ValueError("Оценка должна быть целым числом от 2 до 5.")
    if not 2 <= grade <= 5:
        raise ValueError("Оценка должна быть от 2 до 5.")
    return subject, grade


def handle_request(method, path, headers, body):
    if method == "GET":
        if path in ("/", "/grades"):
            return make_response("200 OK", render_page())
        return make_response("404 Not Found", "<h1>404 — страница не найдена</h1>")

    if method == "POST":
        if path != "/grades":
            return make_response("404 Not Found", "<h1>404 — адрес не найден</h1>")
        try:
            subject, grade = parse_grade(body, headers)
            gradebook.setdefault(subject, []).append(grade)
            page = render_page(f"Оценка {grade} по предмету «{subject}» сохранена.")
            return make_response("200 OK", page)
        except (ValueError, UnicodeError, json.JSONDecodeError) as error:
            return make_response("400 Bad Request", render_page(f"Ошибка: {error}"))

    return make_response(
        "405 Method Not Allowed",
        "<h1>405 — используйте GET или POST</h1>",
    )


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)
        print(f"Сервер журнала запущен: http://{HOST}:{PORT}/")
        print("Откройте адрес в браузере. Остановка: Ctrl+C.")

        while True:
            connection, address = server_socket.accept()
            with connection:
                try:
                    request = read_request(connection)
                    if request is None:
                        continue
                    method, path, headers, body = request
                    print(f"{address} — {method} {path}")
                    response = handle_request(method, path, headers, body)
                except (ValueError, OSError) as error:
                    response = make_response(
                        "400 Bad Request",
                        f"<h1>400 — некорректный запрос</h1><p>{escape(str(error))}</p>",
                    )
                connection.sendall(response)


if __name__ == "__main__":
    main()
