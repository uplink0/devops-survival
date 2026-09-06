from datetime import datetime
from pydantic import BaseModel,EmailStr,Field
class RegisterIn(BaseModel):username:str=Field(min_length=3,max_length=32,pattern=r'^[A-Za-z0-9_]+$');email:EmailStr;password:str=Field(min_length=8,max_length=128)
class LoginIn(BaseModel):login:str=Field(min_length=3,max_length=255);password:str=Field(min_length=8,max_length=128)
class ProgressIn(BaseModel):incident_id:str=Field(min_length=1,max_length=64);solved:bool;score:int=Field(ge=0,le=100000)
class ChatIn(BaseModel):content:str=Field(min_length=1,max_length=4000)
class ChatOut(BaseModel):id:int;role:str;content:str;created_at:datetime
