"""Тесты строчного протокола TCP-чата."""

import socket
import unittest

from socket_lab.protocol import MAX_MESSAGE_BYTES, receive_line, send_line


class ProtocolTests(unittest.TestCase):
    """Проверки кодирования, границ сообщения и завершения строки."""

    def test_round_trip(self):
        """UTF-8 сообщение передаётся без искажений."""
        sender, receiver = socket.socketpair()

        with sender, receiver:
            send_line(sender, "Привет")
            self.assertEqual(receive_line(receiver), "Привет")

    def test_message_limit(self):
        """Сообщение длиннее лимита отклоняется до отправки."""
        sender, receiver = socket.socketpair()

        with sender, receiver:
            with self.assertRaises(ValueError):
                send_line(sender, "a" * (MAX_MESSAGE_BYTES + 1))

    def test_multiline_message_is_rejected(self):
        """Одно сообщение не может нарушить границы строчного протокола."""
        sender, receiver = socket.socketpair()

        with sender, receiver:
            with self.assertRaises(ValueError):
                send_line(sender, "первая\nвторая")


if __name__ == "__main__":
    unittest.main()
