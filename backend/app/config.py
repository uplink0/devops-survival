from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url:str='postgresql+psycopg://devops:devops@db:5432/devops_survival'
    jwt_secret:str='CHANGE_ME_IN_PRODUCTION'
    jwt_algorithm:str='HS256'
    access_token_minutes:int=10080
    cors_origins:str='*'
    upload_dir:str='/app/uploads'
    public_base_url:str=''
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
settings=Settings()
