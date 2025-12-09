from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from pathlib import Path

# 載入環境變數
load_dotenv()

# 資料庫設定
DB_URL = os.getenv("DB_URL", "sqlite:///./hrms.db")
if DB_URL.startswith("sqlite:///") and not DB_URL.startswith("sqlite:////"):
    # 相對路徑轉換為絕對路徑
    db_path = Path(DB_URL.replace("sqlite:///", ""))
    if not db_path.is_absolute():
        db_path = Path(__file__).parent / db_path
    DB_URL = f"sqlite:///{db_path}"

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session() -> Session:
    """取得資料庫 Session"""
    return SessionLocal()

