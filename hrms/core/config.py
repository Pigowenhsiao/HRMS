from pydantic import BaseModel
from dotenv import load_dotenv
import os, yaml

load_dotenv()

class CSVSettings(BaseModel):
    data_dir: str = os.getenv("HRMS_CSV_DATA_DIR", "./data")

class DBSettings(BaseModel):
    backend: str = os.getenv("HRMS_DB_BACKEND", "csv")
    csv: CSVSettings = CSVSettings()

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "HRMS Multi-Backend")
    database: DBSettings = DBSettings()
    # Access 資料庫路徑
    access_db_path: str = os.getenv("ACCESS_DB_PATH", "./hrms.mdb")

def load_settings_from_yaml(path: str = "config/settings.yaml") -> Settings:
    base = Settings()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        # 混入 YAML 設定（以 .env 為優先）
        if "database" in data and "csv" in data["database"]:
            base.database.csv.data_dir = data["database"]["csv"].get("data_dir", base.database.csv.data_dir)
        if "app_name" in data:
            base.app_name = data["app_name"] or base.app_name
    return base

settings = load_settings_from_yaml()
