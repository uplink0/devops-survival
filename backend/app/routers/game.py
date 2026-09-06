from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter,Depends,File,HTTPException,UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import current_user
from ..config import settings
from ..db import get_db
from ..models import ChatMessage,Companion,InventoryItem,Progress,User
from ..schemas import ChatIn,CharacterIn,ProgressIn,ShopBuyIn
router=APIRouter(prefix='/api',tags=['game'])
SHOP_ITEMS={
 'potion':{'name':'Зелье лечения','icon':'🧪','price':20,'description':'Восстанавливает 20 HP.','category':'Расходуемое'},
 'torch':{'name':'Факел','icon':'🔥','price':8,'description':'Освещает тёмные места.','category':'Снаряжение'},
 'dagger':{'name':'Кинжал','icon':'🗡️','price':35,'description':'Простой кинжал. Урон 1d4 колющего.','category':'Оружие'},
 'shortsword':{'name':'Короткий меч','icon':'⚔️','price':60,'description':'Надёжное лёгкое оружие. Урон 1d6 колющего.','category':'Оружие'},
 'leather_armor':{'name':'Кожаная броня','icon':'🥋','price':75,'description':'Лёгкая защита для странника. Класс брони +1.','category':'Броня'},
 'mana_scroll':{'name':'Свиток искры','icon':'📜','price':45,'description':'Одноразовый магический свиток.','category':'Магия'},
 'antidote':{'name':'Противоядие','icon':'🧴','price':30,'description':'Снимает обычное отравление.','category':'Расходуемое'},
 'rope':{'name':'Верёвка','icon':'🪢','price':12,'description':'10 метров крепкой пеньковой верёвки.','category':'Снаряжение'}
}
def public_user(u:User):
 return {'id':u.id,'username':u.username,'email':u.email,'xp':u.xp,'streak':u.streak,'gold':u.gold,'created_at':u.created_at,'avatar_url':u.avatar_url,'character':None if not u.character_name else {'name':u.character_name,'race':u.character_race,'class':u.character_class,'background':u.character_background,'stats':{'strength':u.strength,'dexterity':u.dexterity,'constitution':u.constitution,'intelligence':u.intelligence,'wisdom':u.wisdom,'charisma':u.charisma}}}
def ensure_companions(user:User,db:Session):
 if not db.scalar(select(Companion).where(Companion.user_id==user.id)):
  db.add_all([Companion(user_id=user.id,name='Лира',role='Следопыт',emoji='🏹',description='Тихая и наблюдательная. Хорошо читает следы.',hp=82),Companion(user_id=user.id,name='Борин',role='Воин',emoji='🛡️',description='Держит строй и принимает удар на себя.',hp=100)])
  db.commit()
@router.get('/profile')
def profile(user:User=Depends(current_user),db:Session=Depends(get_db)):
 rows=db.scalars(select(Progress).where(Progress.user_id==user.id).order_by(Progress.last_played.desc())).all();return {'user':public_user(user),'progress':[{'incident_id':r.incident_id,'solved':r.solved,'best_score':r.best_score,'attempts':r.attempts,'last_played':r.last_played} for r in rows]}
@router.post('/character')
def create_character(data:CharacterIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 if user.character_name:raise HTTPException(409,'Персонаж уже создан')
 user.character_name=data.name.strip();user.character_race=data.race.strip();user.character_class=data.character_class.strip();user.character_background=data.background.strip();user.strength=data.strength;user.dexterity=data.dexterity;user.constitution=data.constitution;user.intelligence=data.intelligence;user.wisdom=data.wisdom;user.charisma=data.charisma;user.gold=100
 db.query(InventoryItem).filter(InventoryItem.user_id==user.id).delete(synchronize_session=False)
 db.commit();db.refresh(user);return public_user(user)
@router.delete('/character')
def delete_character(user:User=Depends(current_user),db:Session=Depends(get_db)):
 if not user.character_name:raise HTTPException(404,'Персонаж не создан')
 for field in ['character_name','character_race','character_class','character_background','strength','dexterity','constitution','intelligence','wisdom','charisma']:setattr(user,field,None)
 user.gold=0
 db.query(InventoryItem).filter(InventoryItem.user_id==user.id).delete(synchronize_session=False)
 db.commit();db.refresh(user);return public_user(user)
@router.post('/progress')
def save_progress(data:ProgressIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 row=db.scalar(select(Progress).where(Progress.user_id==user.id,Progress.incident_id==data.incident_id))
 if not row:row=Progress(user_id=user.id,incident_id=data.incident_id);db.add(row)
 row.attempts+=1;row.solved=row.solved or data.solved;row.best_score=max(row.best_score,data.score);db.flush();user.xp=sum(x.best_score for x in user.progress);db.commit();return {'ok':True,'xp':user.xp}
@router.get('/leaderboard')
def leaderboard(db:Session=Depends(get_db)):
 users=db.scalars(select(User).order_by(User.xp.desc(),User.created_at.asc()).limit(50)).all();return [{'rank':i+1,'username':u.username,'xp':u.xp,'streak':u.streak} for i,u in enumerate(users)]
@router.get('/inventory')
def inventory(user:User=Depends(current_user),db:Session=Depends(get_db)):
 return [{'id':x.id,'item_key':x.item_key,'name':x.name,'icon':x.icon,'quantity':x.quantity,'description':x.description} for x in db.scalars(select(InventoryItem).where(InventoryItem.user_id==user.id,InventoryItem.quantity>0).order_by(InventoryItem.id)).all()]
@router.get('/shop')
def shop(user:User=Depends(current_user)):
 return {'gold':user.gold,'items':[{'item_key':key,**item} for key,item in SHOP_ITEMS.items()]}
@router.post('/shop/buy')
def buy_shop_item(data:ShopBuyIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 if not user.character_name:raise HTTPException(400,'Сначала создай персонажа')
 item=SHOP_ITEMS.get(data.item_key)
 if not item:raise HTTPException(404,'Предмет не найден в магазине')
 if user.gold<item['price']:raise HTTPException(400,'Недостаточно золота')
 existing=db.scalar(select(InventoryItem).where(InventoryItem.user_id==user.id,InventoryItem.item_key==data.item_key))
 if existing:existing.quantity+=1
 else:db.add(InventoryItem(user_id=user.id,item_key=data.item_key,name=item['name'],icon=item['icon'],quantity=1,description=item['description']))
 user.gold-=item['price'];db.commit();db.refresh(user)
 rows=db.scalars(select(InventoryItem).where(InventoryItem.user_id==user.id,InventoryItem.quantity>0).order_by(InventoryItem.id)).all()
 return {'gold':user.gold,'inventory':[{'id':x.id,'item_key':x.item_key,'name':x.name,'icon':x.icon,'quantity':x.quantity,'description':x.description} for x in rows]}
@router.get('/companions')
def companions(user:User=Depends(current_user),db:Session=Depends(get_db)):
 ensure_companions(user,db);return [{'id':x.id,'name':x.name,'role':x.role,'emoji':x.emoji,'description':x.description,'hp':x.hp} for x in db.scalars(select(Companion).where(Companion.user_id==user.id)).all()]
@router.get('/chat')
def chat(user:User=Depends(current_user),db:Session=Depends(get_db)):return [{'id':x.id,'role':x.role,'content':x.content,'created_at':x.created_at} for x in db.scalars(select(ChatMessage).where(ChatMessage.user_id==user.id).order_by(ChatMessage.created_at.asc()).limit(100)).all()]
@router.post('/chat')
def send_chat(data:ChatIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 msg=ChatMessage(user_id=user.id,role='user',content=data.content.strip());db.add(msg);db.commit();db.refresh(msg);return {'id':msg.id,'role':msg.role,'content':msg.content,'created_at':msg.created_at}
@router.post('/avatar')
async def avatar(file:UploadFile=File(...),user:User=Depends(current_user),db:Session=Depends(get_db)):
 allowed={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}
 if file.content_type not in allowed:raise HTTPException(400,'Only JPEG, PNG and WebP are allowed')
 data=await file.read()
 if len(data)>5*1024*1024:raise HTTPException(413,'Avatar is too large (max 5 MB)')
 root=Path(settings.upload_dir)/'avatars';root.mkdir(parents=True,exist_ok=True);name=f'{user.id}-{uuid4().hex}{allowed[file.content_type]}';(root/name).write_bytes(data);user.avatar_url=f'/uploads/avatars/{name}';db.commit();return {'avatar_url':user.avatar_url}
