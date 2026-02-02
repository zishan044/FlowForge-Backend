from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config= ConfigDict(env_file='.env')

    DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flowforge"
    REDIS_URL: str = "redis://:password@localhost:6379/0"
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_DEFAULT_TTL: int = 60
    
settings = Settings()
