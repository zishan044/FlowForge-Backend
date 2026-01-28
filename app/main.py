from fastapi import FastAPI

from app.api.routers import project_router, task_router, auth_router, project_invite_router

app = FastAPI(title='FlowForge')

app.include_router(project_router)
app.include_router(project_invite_router)
app.include_router(task_router)
app.include_router(auth_router)

@app.get('/health')
async def health():
    return {'status': 'ok'}