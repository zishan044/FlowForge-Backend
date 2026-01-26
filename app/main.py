from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from contextlib import asynccontextmanager

from app.api.routers import project_router, task_router, auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n🔥 DEBUG: SQLAlchemy is trying to connect to: {engine.url}\n")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title='FlowForge', lifespan=lifespan)

app.include_router(project_router)
app.include_router(task_router)
app.include_router(auth_router)

@app.get('/health')
async def health():
    return {'status': 'ok'}