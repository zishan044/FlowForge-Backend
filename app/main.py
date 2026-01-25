from fastapi import FastAPI

app = FastAPI(title='FlowForge')

@app.get('/health')
async def health():
    return {'status': 'ok'}