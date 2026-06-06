from fastapi import FastAPI

from app.config import SERVER_NAME
from app.ws import router as websocket_router

app = FastAPI(title=SERVER_NAME)
app.include_router(websocket_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": SERVER_NAME,
    }
