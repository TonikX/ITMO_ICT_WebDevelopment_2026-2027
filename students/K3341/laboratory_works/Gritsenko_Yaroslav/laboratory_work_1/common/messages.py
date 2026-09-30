import json


def send_message(connection, message):
    data = json.dumps(message, ensure_ascii=False).encode("utf-8")
    connection.sendall(data + b"\n")


def receive_message(stream):
    line = stream.readline()
    return json.loads(line) if line else None
