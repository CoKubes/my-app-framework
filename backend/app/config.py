from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Force-load the .env file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

# Debug: Print the absolute path to the .env file
print(f"Looking for .env file at: {env_path}")

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    debug: bool = True
    redis_url: str = os.getenv("REDIS_URL")

    class Config:
        env_file = env_path  # Ensure Pydantic loads from .env

settings = Settings()

# Debug: Print the loaded Redis URL
print(f"Loaded REDIS_URL: {settings.redis_url}")
