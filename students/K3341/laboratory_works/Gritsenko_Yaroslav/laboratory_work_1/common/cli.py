import argparse


def network_parser(port):
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="Адрес сервера")
    parser.add_argument("--port", type=int, default=port, help="Порт сервера")
    return parser
