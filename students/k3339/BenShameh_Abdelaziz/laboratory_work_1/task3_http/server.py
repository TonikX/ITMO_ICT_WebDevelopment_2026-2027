import socket
import os

HOST = "127.0.0.1"
PORT = 5002
HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")

def build_http_response(body: str) -> bytes:
    # An HTTP response is just plain text with a strict shape:
    #   status line
    #   headers
    #   <blank line>
    #   body
    body_bytes = body.encode("utf-8")
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body_bytes

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[SERVER] HTTP server listening on http://{HOST}:{PORT}")

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    conn, addr = server_socket.accept()
    print(f"[SERVER] Connection from {addr}")

    with conn:
        request = conn.recv(4096).decode(errors="ignore")
        print(f"[SERVER] Raw request:\n{request.splitlines()[0] if request else '(empty)'}")

        response = build_http_response(html_content)
        conn.sendall(response)
        print("[SERVER] Sent HTML response")

    server_socket.close()

if __name__ == "__main__":
    main()
