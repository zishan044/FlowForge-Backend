from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n🔥 DEBUG: SQLAlchemy is trying to connect to: {engine.url}\n")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title='FlowForge', lifespan=lifespan)

@app.get('/health')
async def health():
    return {'status': 'ok'}