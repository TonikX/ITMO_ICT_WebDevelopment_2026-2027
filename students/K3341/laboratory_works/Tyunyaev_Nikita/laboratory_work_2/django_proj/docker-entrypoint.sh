#!/usr/bin/env bash
set -e

echo "=== Ожидание готовности PostgreSQL на ${POSTGRES_SERVER}:${POSTGRES_PORT} ==="
until pg_isready --host="${POSTGRES_SERVER:-db}" --port="${POSTGRES_PORT:-5432}" --username="${POSTGRES_USER:-postgres}"; do
  echo "Ожидание СУБД..."
  sleep 1
done

echo "=== Применение миграций Django ==="
python manage.py makemigrations
python manage.py migrate

echo "=== Инициализация демонстрационных данных ==="
python manage.py init_data

echo "=== Запуск веб-сервера Django ==="
exec python manage.py runserver 0.0.0.0:8000
