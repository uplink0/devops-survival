from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from .config import settings
from .db import engine
from . import models
from .routers.auth import router as auth_router
from .routers.game import router as game_router
from .routers.rules import router as rules_router
from .routers.ai import router as ai_router

app=FastAPI(title='DND Adventure API',version='2.2.0')
origins=[x.strip() for x in settings.cors_origins.split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins or ['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
Path(settings.upload_dir).mkdir(parents=True,exist_ok=True)
app.mount('/uploads',StaticFiles(directory=settings.upload_dir),name='uploads')
app.include_router(auth_router);app.include_router(game_router);app.include_router(rules_router);app.include_router(ai_router)

@app.get('/api/health')
def health():
 try:
  with engine.connect() as conn:conn.execute(text('SELECT 1'))
  return {'status':'ok','database':'ok'}
 except Exception:return {'status':'degraded','database':'unavailable'}
