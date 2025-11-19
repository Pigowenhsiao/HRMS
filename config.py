from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "HRMS")
    db_url: str = os.getenv("DB_URL", "sqlite:///./hrms.sqlite3")

settings = Settings()
