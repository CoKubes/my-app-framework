from fastapi import FastAPI
from app.routes import items
from app.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(items.router)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.app_name}!"}