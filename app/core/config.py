from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config= ConfigDict(env_file='.env')

    DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flowforge"
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
settings = Settings()
