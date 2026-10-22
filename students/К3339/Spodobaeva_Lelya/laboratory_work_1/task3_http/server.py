from pathlib import Path
import socket


HOST = "127.0.0.1"
PORT = 5003
BUFFER_SIZE = 1024
BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"


def build_response():
    body = INDEX_FILE.read_bytes()
    headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/html; charset=utf-8",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("utf-8") + body


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Открой http://{HOST}:{PORT} в браузере")

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                request = client_socket.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
                print(f"Request from {client_address}:")
                print(request.splitlines()[0] if request else "Empty request")
                client_socket.sendall(build_response())


if __name__ == "__main__":
    main()
