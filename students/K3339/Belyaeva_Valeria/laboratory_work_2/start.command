#!/bin/zsh
set -e
cd "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
export PATH="/opt/homebrew/opt/postgresql@16/bin:/usr/local/opt/postgresql@16/bin:$PATH"
if ! command -v pg_ctl >/dev/null; then
  echo 'Нужен PostgreSQL 16: brew install postgresql@16'
  exit 1
fi
mkdir -p .runtime
if [[ ! -f .runtime/postgres/PG_VERSION ]]; then
  initdb -D .runtime/postgres -A trust -U web_lab --no-locale -E UTF8
fi
if ! pg_ctl -D .runtime/postgres status >/dev/null 2>&1; then
  pg_ctl -D .runtime/postgres -l .runtime/postgres.log -o '-p 55432 -h 127.0.0.1' start
fi
if ! psql -h 127.0.0.1 -p 55432 -U web_lab postgres -Atc "SELECT 1 FROM pg_database WHERE datname='nordline'" | grep -q 1; then
  createdb -h 127.0.0.1 -p 55432 -U web_lab nordline
fi
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
echo 'Сайт: http://127.0.0.1:8002'
echo 'Доступы: .runtime/access.txt'
open http://127.0.0.1:8002
.venv/bin/python manage.py runserver 127.0.0.1:8002
