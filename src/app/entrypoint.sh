#!/bin/sh
set -e

echo "Waiting for postgres..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  sleep 1
done
echo "Postgres is up!"

echo "Initializing database and seeding data..."
python -c "from src.shared.initialize import init_db; init_db()"

exec "$@"
