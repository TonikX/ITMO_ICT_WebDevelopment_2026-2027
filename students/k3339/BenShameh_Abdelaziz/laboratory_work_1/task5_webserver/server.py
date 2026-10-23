import socket
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 5004


grades = {}

def render_page() -> str:
    rows = ""
    for subject, grade_list in grades.items():
        rows += f"<tr><td>{subject}</td><td>{', '.join(str(g) for g in grade_list)}</td></tr>\n"

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Grades Journal</title></head>
<body>
    <h1>Grades Journal</h1>
    <table border="1" cellpadding="6">
        <tr><th>Subject</th><th>Grades</th></tr>
        {rows if rows else '<tr><td colspan="2">No grades yet</td></tr>'}
    </table>

    <h2>Add a grade</h2>
    <form method="POST" action="/">
        <input type="text" name="subject" placeholder="Subject" required>
        <input type="number" name="grade" placeholder="Grade" required>
        <button type="submit">Submit</button>
    </form>
</body>
</html>"""

def build_response(status_line: str, body: str) -> bytes:
    body_bytes = body.encode("utf-8")
    headers = (
        f"{status_line}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body_bytes

def handle_request(request_text: str) -> bytes:
    lines = request_text.split("\r\n")
    method, path, _ = lines[0].split(" ")

    if method == "GET":
        return build_response("HTTP/1.1 200 OK", render_page())

    elif method == "POST":
        header_part, _, body = request_text.partition("\r\n\r\n")

        fields = parse_qs(body)
        subject = fields.get("subject", [""])[0].strip()
        grade = fields.get("grade", [""])[0].strip()

        if subject and grade:
            grades.setdefault(subject, []).append(grade)
            print(f"[SERVER] Added grade {grade} for {subject}. Journal: {grades}")

        return build_response("HTTP/1.1 200 OK", render_page())

    else:
        return build_response("HTTP/1.1 405 Method Not Allowed", "<h1>405 Method Not Allowed</h1>")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER] Grades web server listening on http://{HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        with conn:
            request = conn.recv(8192).decode(errors="ignore")
            if not request:
                continue

            response = handle_request(request)
            conn.sendall(response)

if __name__ == "__main__":
    main()
