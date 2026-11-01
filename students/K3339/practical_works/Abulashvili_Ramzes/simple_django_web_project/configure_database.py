import getpass
import json
import secrets
from pathlib import Path

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / "database.local.json"


def main():
    databases = []
    if (ROOT / "practice/manage.py").exists() or (ROOT / "project_first_app/models.py").exists():
        databases.append("web_lab_2_practice")
    if (ROOT / "conference_project/manage.py").exists() or (ROOT / "conferences/models.py").exists():
        databases.append("web_lab_2_conferences")
    if not databases:
        raise SystemExit("Запустите скрипт из папки с проектом Django.")
    default_user = databases[0] if len(databases) == 1 else "web_lab_2"
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {
        "host": "127.0.0.1", "port": 5432, "user": default_user, "password": secrets.token_urlsafe(24),
    }
    password = getpass.getpass("Пароль пользователя postgres: ")
    with psycopg.connect(host=config["host"], port=config["port"], dbname="postgres", user="postgres", password=password, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [config["user"]])
            if not cursor.fetchone():
                cursor.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(config["user"]), sql.Literal(config["password"])))
            for database in databases:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [database])
                if not cursor.fetchone():
                    cursor.execute(sql.SQL("CREATE DATABASE {} OWNER {} ENCODING 'UTF8' TEMPLATE template0").format(sql.Identifier(database), sql.Identifier(config["user"])))
                with psycopg.connect(host=config["host"], port=config["port"], dbname=database, user=config["user"], password=config["password"]):
                    print(f"База готова: {database}")
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Настройки сохранены в database.local.json. Теперь примените миграции проектов.")


if __name__ == "__main__":
    try:
        main()
    except (psycopg.Error, OSError) as error:
        print(f"Не удалось настроить PostgreSQL: {error}")
        raise SystemExit(1)
