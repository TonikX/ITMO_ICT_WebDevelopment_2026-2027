"""Тесты TCP-операции варианта №2 из задания №2."""

import socket
import threading
import unittest

from socket_lab.math_client import request_triangle_area
from socket_lab.math_server import (
    calculate_triangle_area,
    handle_client,
    process_request,
)


class TriangleAreaTests(unittest.TestCase):
    """Проверки вычисления и обмена данными по TCP."""

    def test_triangle_area_is_calculated(self):
        """Площадь равна половине произведения основания и высоты."""
        self.assertEqual(calculate_triangle_area(3, 4), 6)

    def test_non_positive_dimension_is_rejected(self):
        """Неположительная длина не используется в вычислении."""
        with self.assertRaises(ValueError):
            calculate_triangle_area(0, 4)

    def test_invalid_request_returns_error(self):
        """Некорректное количество параметров возвращает понятную ошибку."""
        self.assertTrue(process_request("3").startswith("ERROR:"))

    def test_tcp_client_receives_area_from_server(self):
        """Клиент получает результат от обработчика через TCP-соединение."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", 0))
            server.listen(1)
            host, port = server.getsockname()[:2]

            def run_server() -> None:
                connection, _ = server.accept()
                with connection:
                    handle_client(connection)

            server_thread = threading.Thread(target=run_server)
            server_thread.start()
            response = request_triangle_area(host, port, 3, 4)
            server_thread.join(timeout=1)

        self.assertFalse(server_thread.is_alive())
        self.assertEqual(response, "Площадь треугольника: 6")


if __name__ == "__main__":
    unittest.main()
