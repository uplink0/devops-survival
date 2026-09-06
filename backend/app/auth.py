from datetime import datetime,timedelta,timezone
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from jose import JWTError,jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User
password_hash=PasswordHash.recommended();bearer=HTTPBearer(auto_error=False)
def make_token(user:User)->str:
 now=datetime.now(timezone.utc);return jwt.encode({'sub':str(user.id),'username':user.username,'exp':now+timedelta(minutes=settings.access_token_minutes)},settings.jwt_secret,algorithm=settings.jwt_algorithm)
def current_user(credentials:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db))->User:
 if not credentials:raise HTTPException(status_code=401,detail='Authentication required')
 try:user_id=int(jwt.decode(credentials.credentials,settings.jwt_secret,algorithms=[settings.jwt_algorithm]).get('sub','0'))
 except(JWTError,ValueError):raise HTTPException(status_code=401,detail='Invalid or expired token')
 user=db.get(User,user_id)
 if not user:raise HTTPException(status_code=401,detail='User not found')
 return user
