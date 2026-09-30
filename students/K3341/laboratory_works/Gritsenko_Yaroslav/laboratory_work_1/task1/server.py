import socket

from laboratory_work_1.common.cli import network_parser


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((host, port))
        print(f"UDP-сервер: {host}:{server.getsockname()[1]}")
        while True:
            data, address = server.recvfrom(4096)
            print(f"{address}: {data.decode('utf-8', errors='replace')}")
            server.sendto(b"Hello, client", address)


if __name__ == "__main__":
    args = network_parser(9001).parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
