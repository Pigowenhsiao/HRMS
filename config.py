from pydantic import BaseModel
from dotenv import load_dotenv
import os
import yaml
from pathlib import Path

load_dotenv()

class DatabaseConfig(BaseModel):
    backend: str = os.getenv("HRMS_DB_BACKEND", "csv")
    csv: dict = {"data_dir": os.getenv("HRMS_CSV_DATA_DIR", "./data")}

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "HRMS")
    database: DatabaseConfig = DatabaseConfig()
    # Access 資料庫路徑
    access_db_path: str = os.getenv("ACCESS_DB_PATH", "./hrms.mdb")
    # 原有的資料庫 URL (用於其他類型的資料庫)
    db_url: str = os.getenv("DB_URL", "sqlite:///./hrms.sqlite3")

settings = Settings()
