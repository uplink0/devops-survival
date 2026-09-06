from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter,Depends,File,HTTPException,UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import current_user
from ..config import settings
from ..db import get_db
from ..models import ChatMessage,Companion,InventoryItem,Progress,User
from ..schemas import ChatIn,ProgressIn
router=APIRouter(prefix='/api',tags=['game'])
def public_user(u:User):return {'id':u.id,'username':u.username,'email':u.email,'xp':u.xp,'streak':u.streak,'created_at':u.created_at,'avatar_url':u.avatar_url}
@router.get('/profile')
def profile(user:User=Depends(current_user),db:Session=Depends(get_db)):
 rows=db.scalars(select(Progress).where(Progress.user_id==user.id).order_by(Progress.last_played.desc())).all();return {'user':public_user(user),'progress':[{'incident_id':r.incident_id,'solved':r.solved,'best_score':r.best_score,'attempts':r.attempts,'last_played':r.last_played} for r in rows]}
@router.post('/progress')
def save_progress(data:ProgressIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 row=db.scalar(select(Progress).where(Progress.user_id==user.id,Progress.incident_id==data.incident_id))
 if not row:row=Progress(user_id=user.id,incident_id=data.incident_id);db.add(row)
 row.attempts+=1;row.solved=row.solved or data.solved;row.best_score=max(row.best_score,data.score);db.flush();user.xp=sum(x.best_score for x in user.progress);db.commit();return {'ok':True,'xp':user.xp}
@router.get('/leaderboard')
def leaderboard(db:Session=Depends(get_db)):
 users=db.scalars(select(User).order_by(User.xp.desc(),User.created_at.asc()).limit(50)).all();return [{'rank':i+1,'username':u.username,'xp':u.xp,'streak':u.streak} for i,u in enumerate(users)]
@router.get('/inventory')
def inventory(user:User=Depends(current_user),db:Session=Depends(get_db)):return [{'id':x.id,'item_key':x.item_key,'name':x.name,'icon':x.icon,'quantity':x.quantity,'description':x.description} for x in db.scalars(select(InventoryItem).where(InventoryItem.user_id==user.id)).all()]
@router.get('/companions')
def companions(user:User=Depends(current_user),db:Session=Depends(get_db)):return [{'id':x.id,'name':x.name,'role':x.role,'emoji':x.emoji,'description':x.description,'hp':x.hp} for x in db.scalars(select(Companion).where(Companion.user_id==user.id)).all()]
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
