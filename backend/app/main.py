from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings
from pwdlib import PasswordHash
from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://devops:devops@db:5432/devops_survival"
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 10080
    cors_origins: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    xp: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    progress: Mapped[list[Progress]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Progress(Base):
    __tablename__ = "progress"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    incident_id: Mapped[str] = mapped_column(String(64), index=True)
    solved: Mapped[bool] = mapped_column(default=False)
    best_score: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_played: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user: Mapped[User] = relationship(back_populates="progress")


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    login: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class ProgressIn(BaseModel):
    incident_id: str = Field(min_length=1, max_length=64)
    solved: bool
    score: int = Field(ge=0, le=100000)


app = FastAPI(title="DevOps Survival API", version="1.0.0")
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def token_for(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user.id), "username": user.username, "exp": now + timedelta(minutes=settings.access_token_minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), session: Session = Depends(db)) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = int(payload.get("sub", "0"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)


@app.get("/api/health")
def health() -> dict:
    try:
        with Session(engine) as session:
            session.execute(select(1))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}


def user_public(user: User) -> dict:
    return {"id": user.id, "username": user.username, "email": user.email, "xp": user.xp, "streak": user.streak, "created_at": user.created_at}


def progress_public(row: Progress) -> dict:
    return {"incident_id": row.incident_id, "solved": row.solved, "best_score": row.best_score, "attempts": row.attempts, "last_played": row.last_played}


@app.post("/api/auth/register")
def register(data: RegisterIn, session: Session = Depends(db)) -> dict:
    username = data.username.strip()
    email = str(data.email).lower().strip()
    if session.scalar(select(User).where(User.username == username)):
        raise HTTPException(409, "Username already exists")
    if session.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already exists")
    user = User(username=username, email=email, password_hash=password_hash.hash(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"access_token": token_for(user), "token_type": "bearer", "user": user_public(user)}


@app.post("/api/auth/login")
def login(data: LoginIn, session: Session = Depends(db)) -> dict:
    login_value = data.login.strip()
    user = session.scalar(select(User).where((User.username == login_value) | (User.email == login_value.lower())))
    if not user or not password_hash.verify(data.password, user.password_hash):
        raise HTTPException(401, "Invalid username/email or password")
    return {"access_token": token_for(user), "token_type": "bearer", "user": user_public(user)}


@app.get("/api/auth/me")
def me(user: User = Depends(current_user)) -> dict:
    return user_public(user)


@app.get("/api/profile")
def profile(user: User = Depends(current_user), session: Session = Depends(db)) -> dict:
    rows = session.scalars(select(Progress).where(Progress.user_id == user.id).order_by(Progress.last_played.desc())).all()
    return {"user": user_public(user), "progress": [progress_public(x) for x in rows]}


@app.post("/api/progress")
def save_progress(data: ProgressIn, user: User = Depends(current_user), session: Session = Depends(db)) -> dict:
    row = session.scalar(select(Progress).where(Progress.user_id == user.id, Progress.incident_id == data.incident_id))
    if not row:
        row = Progress(user_id=user.id, incident_id=data.incident_id)
        session.add(row)
    row.attempts += 1
    row.solved = row.solved or data.solved
    row.best_score = max(row.best_score, data.score)
    row.last_played = datetime.now(timezone.utc)
    session.flush()
    user.xp = sum(x.best_score for x in user.progress)
    if data.solved:
        user.streak = max(user.streak, 1)
    session.commit()
    session.refresh(row)
    return {"progress": progress_public(row), "user": user_public(user)}


@app.get("/api/leaderboard")
def leaderboard(session: Session = Depends(db)) -> list[dict]:
    users = session.scalars(select(User).order_by(User.xp.desc(), User.created_at.asc()).limit(50)).all()
    return [{"rank": i + 1, "username": u.username, "xp": u.xp, "streak": u.streak} for i, u in enumerate(users)]
