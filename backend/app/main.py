from fastapi import FastAPI
from app.routes import items

app = FastAPI()

app.include_router(items.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}