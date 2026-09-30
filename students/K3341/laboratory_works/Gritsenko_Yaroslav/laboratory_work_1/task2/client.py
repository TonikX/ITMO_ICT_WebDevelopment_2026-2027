import socket

from laboratory_work_1.common.cli import network_parser
from laboratory_work_1.common.messages import receive_message, send_message


def request_calculation(host, port, values):
    with socket.create_connection((host, port), timeout=5) as client:
        send_message(client, values)
        with client.makefile("rb") as stream:
            response = receive_message(stream)
        if response is None:
            raise ValueError("Сервер закрыл соединение без ответа")
        return response


def main():
    args = network_parser(9002).parse_args()
    try:
        values = [float(input(f"{label}: ")) for label in
                  ("Первое основание a", "Второе основание b", "Высота h")]
        response = request_calculation(args.host, args.port, values)
        if "error" in response:
            print(f"Ошибка: {response['error']}")
        else:
            print(f"Площадь трапеции: {response['area']:g}")
    except (ValueError, OSError, EOFError) as error:
        raise SystemExit(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
