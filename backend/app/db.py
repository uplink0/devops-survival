from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,Session
from .config import settings
engine=create_engine(settings.database_url,pool_pre_ping=True)
class Base(DeclarativeBase):pass
def get_db()->Generator[Session,None,None]:
    with Session(engine) as session:yield session
