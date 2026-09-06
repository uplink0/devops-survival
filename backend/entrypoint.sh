#!/bin/sh
set -e
if python -c "from sqlalchemy import inspect; from app.db import engine; print('users' in inspect(engine).get_table_names())" | grep -q True; then
  alembic stamp 0001_initial || true
fi
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
