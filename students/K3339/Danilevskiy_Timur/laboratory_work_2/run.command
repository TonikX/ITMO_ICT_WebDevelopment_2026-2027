#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

if command -v python3.10 >/dev/null 2>&1; then
  PYTHON_BIN=python3.10
else
  PYTHON_BIN=python3
fi
"$PYTHON_BIN" -c 'import sys; assert sys.version_info[:2] == (3, 10), "Для Django 3.2 используйте Python 3.10"'

if command -v docker >/dev/null 2>&1; then
  DOCKER_BIN=docker
elif [ -x /Applications/Docker.app/Contents/Resources/bin/docker ]; then
  DOCKER_BIN=/Applications/Docker.app/Contents/Resources/bin/docker
else
  echo "Установите Docker Desktop и включите его перед запуском."
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  "$PYTHON_BIN" -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
fi
"$DOCKER_BIN" compose -p itmo-apex-lab2 up -d --wait
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
echo "Откройте http://127.0.0.1:8000/ . Для остановки нажмите Ctrl+C."
exec .venv/bin/python manage.py runserver 127.0.0.1:8000
