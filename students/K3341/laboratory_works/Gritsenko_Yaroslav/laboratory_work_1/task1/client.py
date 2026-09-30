import socket

from laboratory_work_1.common.cli import network_parser


def exchange(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(5)
        client.sendto(b"Hello, server", (host, port))
        data, _ = client.recvfrom(4096)
        return data.decode("utf-8")


if __name__ == "__main__":
    args = network_parser(9001).parse_args()
    try:
        print(exchange(args.host, args.port))
    except OSError as error:
        raise SystemExit(f"Ошибка обмена с сервером: {error}")
