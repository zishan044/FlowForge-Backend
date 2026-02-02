from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routers import project_router, task_router, auth_router, project_invite_router
from app.core.redis import init_redis, close_redis
from app.core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    setup_logging()
    
    yield
    
    await close_redis()

app = FastAPI(title='FlowForge', lifespan=lifespan)

app.include_router(project_router)
app.include_router(project_invite_router)
app.include_router(task_router)
app.include_router(auth_router)

@app.get('/health')
async def health():
    return {'status': 'ok'}