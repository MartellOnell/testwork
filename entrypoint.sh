#!/bin/sh
# entrypoint.sh - Точка входа для Django приложения с ожиданием PostgreSQL

set -e

echo "Ожидание готовности PostgreSQL..."

# Ожидание доступности PostgreSQL
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL недоступна - ожидание..."
  sleep 1
done

echo "PostgreSQL готова!"

# Применение миграций
echo "Применение миграций базы данных..."
python manage.py migrate --noinput

# Сбор статических файлов (для продакшена)
if [ "$DJANGO_ENV" = "production" ]; then
  echo "Сбор статических файлов..."
  python manage.py collectstatic --noinput
fi

echo "Запуск приложения..."
exec "$@"
