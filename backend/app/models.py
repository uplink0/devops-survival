from datetime import datetime,timezone
from sqlalchemy import Boolean,DateTime,ForeignKey,Integer,String,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .db import Base

def now():return datetime.now(timezone.utc)
class User(Base):
 __tablename__='users'
 id:Mapped[int]=mapped_column(primary_key=True);username:Mapped[str]=mapped_column(String(32),unique=True,index=True);email:Mapped[str]=mapped_column(String(255),unique=True,index=True);password_hash:Mapped[str]=mapped_column(String(255));xp:Mapped[int]=mapped_column(Integer,default=0);streak:Mapped[int]=mapped_column(Integer,default=0);avatar_url:Mapped[str|None]=mapped_column(String(512),nullable=True)
 character_name:Mapped[str|None]=mapped_column(String(80),nullable=True);character_race:Mapped[str|None]=mapped_column(String(80),nullable=True);character_class:Mapped[str|None]=mapped_column(String(80),nullable=True);character_background:Mapped[str|None]=mapped_column(String(160),nullable=True)
 strength:Mapped[int|None]=mapped_column(Integer,nullable=True);dexterity:Mapped[int|None]=mapped_column(Integer,nullable=True);constitution:Mapped[int|None]=mapped_column(Integer,nullable=True);intelligence:Mapped[int|None]=mapped_column(Integer,nullable=True);wisdom:Mapped[int|None]=mapped_column(Integer,nullable=True);charisma:Mapped[int|None]=mapped_column(Integer,nullable=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
 progress:Mapped[list['Progress']]=relationship(back_populates='user',cascade='all, delete-orphan');inventory:Mapped[list['InventoryItem']]=relationship(back_populates='user',cascade='all, delete-orphan');companions:Mapped[list['Companion']]=relationship(back_populates='user',cascade='all, delete-orphan');chat_messages:Mapped[list['ChatMessage']]=relationship(back_populates='user',cascade='all, delete-orphan')
class Progress(Base):
 __tablename__='progress'
 id:Mapped[int]=mapped_column(primary_key=True);user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);incident_id:Mapped[str]=mapped_column(String(64),index=True);solved:Mapped[bool]=mapped_column(Boolean,default=False);best_score:Mapped[int]=mapped_column(Integer,default=0);attempts:Mapped[int]=mapped_column(Integer,default=0);last_played:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now);user:Mapped[User]=relationship(back_populates='progress')
class InventoryItem(Base):
 __tablename__='inventory_items'
 id:Mapped[int]=mapped_column(primary_key=True);user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);item_key:Mapped[str]=mapped_column(String(64));name:Mapped[str]=mapped_column(String(120));icon:Mapped[str]=mapped_column(String(16),default='📦');quantity:Mapped[int]=mapped_column(Integer,default=1);description:Mapped[str|None]=mapped_column(String(500),nullable=True);user:Mapped[User]=relationship(back_populates='inventory')
class Companion(Base):
 __tablename__='companions'
 id:Mapped[int]=mapped_column(primary_key=True);user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);name:Mapped[str]=mapped_column(String(80));role:Mapped[str]=mapped_column(String(80));emoji:Mapped[str]=mapped_column(String(16),default='🧙');description:Mapped[str|None]=mapped_column(String(500),nullable=True);hp:Mapped[int]=mapped_column(Integer,default=100);user:Mapped[User]=relationship(back_populates='companions')
class ChatMessage(Base):
 __tablename__='chat_messages'
 id:Mapped[int]=mapped_column(primary_key=True);user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);role:Mapped[str]=mapped_column(String(20));content:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now);user:Mapped[User]=relationship(back_populates='chat_messages')
