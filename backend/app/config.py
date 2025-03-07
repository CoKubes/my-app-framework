from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Force-load the .env file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    debug: bool = True
    redis_url: str = os.getenv("REDIS_URL")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region: str = os.getenv("AWS_REGION")
    aws_log_group: str = "MyAppLogs"
    aws_log_stream: str = "backend"

    class Config:
        env_file = env_path  # Ensure Pydantic loads from .env

settings = Settings()


