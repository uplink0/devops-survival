#!/bin/sh
set -e
if python -c "from sqlalchemy import inspect; from app.db import engine; t=inspect(engine).get_table_names(); print('users' in t and 'alembic_version' not in t)" | grep -q True; then
  alembic stamp 0001_initial
fi
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
