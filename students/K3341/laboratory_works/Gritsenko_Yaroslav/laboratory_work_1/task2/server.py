import socket

from laboratory_work_1.common.cli import network_parser
from laboratory_work_1.common.messages import receive_message, send_message


def handle(connection):
    connection.settimeout(5)
    with connection.makefile("rb") as stream:
        try:
            request = receive_message(stream)
            if request is None:
                return
            a, b, h = request
            if min(a, b, h) <= 0:
                raise ValueError("Основания и высота должны быть положительными")
            response = {"area": (a + b) * h / 2}
        except ValueError as error:
            response = {"error": str(error)}
        send_message(connection, response)


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"Сервер вычислений: {host}:{server.getsockname()[1]}")
        while True:
            connection, address = server.accept()
            with connection:
                try:
                    handle(connection)
                except OSError as error:
                    print(f"{address}: {error}")


if __name__ == "__main__":
    args = network_parser(9002).parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
