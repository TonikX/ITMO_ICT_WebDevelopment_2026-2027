from html import escape
from pathlib import Path
from urllib.parse import parse_qs

from laboratory_work_1.common.cli import network_parser
from laboratory_work_1.common.http import send_response, serve_http

TEMPLATE = Path(__file__).with_name("index.html")
grades = {}


def page():
    rows = "\n".join(
        f'<tr><th scope="row">{escape(subject)}</th><td>{", ".join(map(str, marks))}</td></tr>'
        for subject, marks in grades.items()
    )
    return TEMPLATE.read_text(encoding="utf-8").replace("{{rows}}", rows)


def handle(connection, method, target, headers, body):
    path = target.partition("?")[0]
    if path not in ("/", "/grades"):
        send_response(connection, 404, "Страница не найдена")
    elif method == "GET":
        send_response(connection, 200, page())
    elif method == "POST" and path == "/grades":
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        subject = form.get("subject", [""])[0].strip()
        grade = int(form.get("grade", [""])[0])
        if not subject or grade not in range(1, 6):
            raise ValueError("Введите предмет и оценку от 1 до 5")
        grades.setdefault(subject, []).append(grade)
        send_response(connection, 303, headers={"Location": "/"})
    else:
        send_response(connection, 405, "Метод не поддерживается")


if __name__ == "__main__":
    args = network_parser(9005).parse_args()
    try:
        serve_http(args.host, args.port, handle)
    except KeyboardInterrupt:
        print("\nСервер остановлен")
