import socket
from http import HTTPStatus


def read_request(connection):
    data = bytearray()
    while b"\r\n\r\n" not in data:
        chunk = connection.recv(4096)
        if not chunk:
            raise ValueError("Незавершённые заголовки")
        data.extend(chunk)
    raw_headers, body = bytes(data).split(b"\r\n\r\n", 1)
    lines = raw_headers.decode("iso-8859-1").split("\r\n")
    method, target, _ = lines[0].split()
    headers = {}
    for line in lines[1:]:
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length < 0:
        raise ValueError("Отрицательный Content-Length")
    while len(body) < length:
        chunk = connection.recv(min(4096, length - len(body)))
        if not chunk:
            raise ValueError("Незавершённое тело запроса")
        body += chunk
    return method, target, headers, body[:length]


def send_response(connection, status, body=b"", content_type="text/html; charset=utf-8", headers=None):
    if isinstance(body, str):
        body = body.encode("utf-8")
    lines = [
        f"HTTP/1.1 {status} {HTTPStatus(status).phrase}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    lines.extend(f"{key}: {value}" for key, value in (headers or {}).items())
    connection.sendall(("\r\n".join(lines) + "\r\n\r\n").encode("ascii") + body)


def serve_http(host, port, handler):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"HTTP-сервер: http://{host}:{server.getsockname()[1]}")
        while True:
            connection, _ = server.accept()
            with connection:
                connection.settimeout(5)
                try:
                    handler(connection, *read_request(connection))
                except ValueError as error:
                    try:
                        send_response(connection, 400, str(error), "text/plain; charset=utf-8")
                    except OSError:
                        pass
                except OSError as error:
                    print(f"Ошибка соединения: {error}")
