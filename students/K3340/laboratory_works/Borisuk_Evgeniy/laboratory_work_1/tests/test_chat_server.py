"""Интеграционные тесты многопользовательского TCP-чата."""

import socket
import threading
import unittest

from socket_lab.chat_server import ChatServer
from socket_lab.protocol import receive_line, send_line


class ChatServerTests(unittest.TestCase):
    """Проверки регистрации клиентов и доставки сообщений."""

    def setUp(self):
        """Запустить сервер на свободном локальном порту."""
        self.server = ChatServer(port=0)
        self.server.start()
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.server_thread.start()

    def tearDown(self):
        """Закрыть сокеты и дождаться завершения серверного потока."""
        self.server.stop()
        self.server_thread.join(timeout=1)

    def connect_client(self, name: str) -> socket.socket:
        """Подключить клиента и завершить обмен приветствиями."""
        client = socket.create_connection(self.server.address, timeout=1)
        self.assertEqual(receive_line(client), "Введите имя:")
        send_line(client, name)
        self.assertEqual(
            receive_line(client),
            "Подключение установлено. /quit — выйти.",
        )
        return client

    def test_message_is_sent_to_another_client(self):
        """Сообщение одного участника получает другой участник."""
        first = self.connect_client("Аня")
        second = self.connect_client("Борис")

        with first, second:
            self.assertIn("Борис присоединился", receive_line(first))
            send_line(first, "Проверка")
            self.assertEqual(receive_line(second), "Аня: Проверка")

    def test_duplicate_name_is_rejected(self):
        """Сервер не регистрирует двух клиентов с одинаковым именем."""
        first = self.connect_client("Аня")
        second = socket.create_connection(self.server.address, timeout=1)

        with first, second:
            self.assertEqual(receive_line(second), "Введите имя:")
            send_line(second, "Аня")
            self.assertEqual(receive_line(second), "Это имя уже занято.")

    def test_blank_name_is_rejected(self):
        """Пустое имя не добавляется в список участников."""
        client = socket.create_connection(self.server.address, timeout=1)

        with client:
            self.assertEqual(receive_line(client), "Введите имя:")
            send_line(client, "   ")
            self.assertEqual(receive_line(client), "Некорректное имя.")


if __name__ == "__main__":
    unittest.main()
