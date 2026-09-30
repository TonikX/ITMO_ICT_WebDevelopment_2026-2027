"""Интеграционный тест UDP-приветствия из задания №1."""

import socket
import threading
import unittest

from socket_lab.udp_client import exchange_greetings
from socket_lab.udp_server import (
    CLIENT_GREETING,
    SERVER_GREETING,
    serve_once,
)


class UdpGreetingTests(unittest.TestCase):
    """Проверка реального обмена датаграммами через localhost."""

    def test_client_and_server_exchange_required_greetings(self):
        """Клиент и сервер получают сообщения из условия задания."""
        received_messages: list[str] = []

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
            server.bind(("127.0.0.1", 0))
            host, port = server.getsockname()[:2]

            def run_server() -> None:
                message, _ = serve_once(server)
                received_messages.append(message)

            server_thread = threading.Thread(target=run_server)
            server_thread.start()
            response = exchange_greetings(host, port)
            server_thread.join(timeout=1)

        self.assertFalse(server_thread.is_alive())
        self.assertEqual(received_messages, [CLIENT_GREETING])
        self.assertEqual(response, SERVER_GREETING)


if __name__ == "__main__":
    unittest.main()
