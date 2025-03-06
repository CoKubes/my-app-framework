from fastapi import FastAPI
from app.routes import items
from app.config import settings
from app.utils.logger import logger

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(items.router)

@app.get("/")
def read_root():
    logger.info("root endpoint hit")
    return {"message": f"Welcome to {settings.app_name}!"}