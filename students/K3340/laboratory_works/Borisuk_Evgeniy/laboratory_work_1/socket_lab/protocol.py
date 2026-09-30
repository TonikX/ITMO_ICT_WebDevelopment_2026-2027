"""Строчный протокол обмена сообщениями для TCP-чата."""

from __future__ import annotations

import socket


ENCODING = "utf-8"
MAX_MESSAGE_BYTES = 4096


def send_line(connection: socket.socket, text: str) -> None:
    """Отправить одно текстовое сообщение, завершённое переводом строки."""
    if "\n" in text or "\r" in text:
        raise ValueError("Сообщение должно занимать ровно одну строку")

    encoded_message = text.encode(ENCODING)
    if len(encoded_message) > MAX_MESSAGE_BYTES:
        raise ValueError(f"Сообщение превышает {MAX_MESSAGE_BYTES} байт")

    connection.sendall(encoded_message + b"\n")


def receive_line(connection: socket.socket) -> str | None:
    """Прочитать одно сообщение или вернуть ``None`` после закрытия сокета."""
    data = bytearray()

    while len(data) <= MAX_MESSAGE_BYTES:
        chunk = connection.recv(1)
        if not chunk:
            return None if not data else data.decode(ENCODING)
        if chunk == b"\n":
            return data.decode(ENCODING).rstrip("\r")
        data.extend(chunk)

    raise ValueError(f"Сообщение превышает {MAX_MESSAGE_BYTES} байт")
