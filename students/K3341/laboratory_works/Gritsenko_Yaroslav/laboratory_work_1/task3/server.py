from pathlib import Path

from laboratory_work_1.common.cli import network_parser
from laboratory_work_1.common.http import send_response, serve_http

INDEX = Path(__file__).with_name("index.html")


def handle(connection, method, target, headers, body):
    if method != "GET":
        send_response(connection, 405, "Используйте GET", headers={"Allow": "GET"})
    elif target.partition("?")[0] not in ("/", "/index.html"):
        send_response(connection, 404, "Страница не найдена")
    else:
        send_response(connection, 200, INDEX.read_bytes())


if __name__ == "__main__":
    args = network_parser(9003).parse_args()
    try:
        serve_http(args.host, args.port, handle)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
