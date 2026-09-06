from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import current_user,make_token,password_hash
from ..db import get_db
from ..models import Companion,InventoryItem,User
from ..schemas import LoginIn,RegisterIn
router=APIRouter(prefix='/api/auth',tags=['auth'])
def public(u:User):return {'id':u.id,'username':u.username,'email':u.email,'xp':u.xp,'streak':u.streak,'created_at':u.created_at,'avatar_url':u.avatar_url,'character':None if not u.character_name else {'name':u.character_name,'race':u.character_race,'class':u.character_class,'background':u.character_background,'stats':{'strength':u.strength,'dexterity':u.dexterity,'constitution':u.constitution,'intelligence':u.intelligence,'wisdom':u.wisdom,'charisma':u.charisma}}}
@router.post('/register')
def register(data:RegisterIn,db:Session=Depends(get_db)):
 username=data.username.strip();email=str(data.email).lower().strip()
 if db.scalar(select(User).where(User.username==username)):raise HTTPException(409,'Username already exists')
 if db.scalar(select(User).where(User.email==email)):raise HTTPException(409,'Email already exists')
 u=User(username=username,email=email,password_hash=password_hash.hash(data.password));db.add(u);db.flush()
 db.add_all([InventoryItem(user_id=u.id,item_key='potion',name='Зелье лечения',icon='🧪',quantity=2,description='Восстанавливает здоровье.'),InventoryItem(user_id=u.id,item_key='torch',name='Факел',icon='🔥',quantity=3,description='Освещает тёмные места.'),InventoryItem(user_id=u.id,item_key='dagger',name='Кинжал',icon='🗡️',quantity=1,description='Простой, но надёжный.'),Companion(user_id=u.id,name='Лира',role='Следопыт',emoji='🏹',description='Тихая и наблюдательная. Хорошо читает следы.',hp=82),Companion(user_id=u.id,name='Борин',role='Воин',emoji='🛡️',description='Держит строй и принимает удар на себя.',hp=100)])
 db.commit();db.refresh(u);return {'access_token':make_token(u),'token_type':'bearer','user':public(u)}
@router.post('/login')
def login(data:LoginIn,db:Session=Depends(get_db)):
 value=data.login.strip();u=db.scalar(select(User).where((User.username==value)|(User.email==value.lower())))
 if not u or not password_hash.verify(data.password,u.password_hash):raise HTTPException(401,'Invalid username/email or password')
 return {'access_token':make_token(u),'token_type':'bearer','user':public(u)}
@router.get('/me')
def me(user:User=Depends(current_user)):return public(user)
