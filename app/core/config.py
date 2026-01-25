from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flowforge"

    class Config:
        env_file = '.env'
    
settings = Settings()
