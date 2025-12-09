#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV → SQLite 遷移工具
將現有的 CSV 檔案資料匯入 SQLite 資料庫，並建立完整的關聯
"""
from __future__ import annotations
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 專案路徑
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SQLITE_PATH = PROJECT_ROOT / "hrms.db"

# 加入專案路徑
sys.path.insert(0, str(PROJECT_ROOT))

from domain.models import (
    Base, create_all_tables, Basic, PersonInfo, Section, Area, Job, VacType, Shift, Shop,
    Certify, CertifyType, CertifyItem, CertifyRecord, TrainingRecord, 
    CertifyToolMap, MustTool, Software, Authority, DelAuthority
)

# CSV 到模型的對映
csv_to_model = {
    # 對照表（無外鍵依賴）
    "L_Section.csv": Section,
    "Area.csv": Area,
    "L_Job.csv": Job,
    "VAC_Type.csv": VacType,
    "SHIFT.csv": Shift,
    "SHOP.csv": Shop,
    "CERTIFY_TYPE.csv": CertifyType,
    "CERTIFY.csv": Certify,  # 證照狀態對照表
    "MUST_TOOL.csv": MustTool,  # 必需工具（注意：全大寫）
    "SOFTWARE.csv": Software,  # 軟體版本
    
    # 主檔
    "BASIC.csv": Basic,
    "CERTIFY_ITEMS.csv": CertifyItem,  # 證照項目主檔
    
    # 子檔（有外鍵依賴）
    "PERSON_INFO.csv": PersonInfo,
    "TRAINING_RECORD.csv": TrainingRecord,  # 主要證照記錄
    "CERTIFY_RECORD.csv": CertifyRecord,  # 次要證照記錄
    "CERTIFY_TOOL_MAP.csv": CertifyToolMap,  # 證照工具對應
    "Authority.csv": Authority,
    "DEL_AUTHORITY.csv": DelAuthority,
    
    # 備份檔案不匯入
    # "BASIC_BACKUP.csv": None,
    # "PERSON_INFO_BACKUP.csv": None,
    # "BASIC2.csv": None,
}

def normalize_boolean(value):
    """標準化布林值"""
    if pd.isna(value) or value == "":
        return True
    str_val = str(value).strip().lower()
    if str_val in ("true", "1", "y", "yes"):
        return True
    elif str_val in ("false", "0", "n", "no", "f"):
        return False
    return True

def normalize_date(value):
    """標準化日期格式"""
    if pd.isna(value) or value == "":
        return None
    # 保持原始格式，交由應用層處理
    return str(value).strip()

def clean_dataframe(df, model_class):
    """清理 DataFrame，符合模型需求"""
    # 轉換欄位名稱
    df.columns = [col.strip() for col in df.columns]
    
    # 特殊欄位名稱對映（CSV 欄位名稱與模型欄位名稱不一致時）
    column_mapping = {}
    
    # 根據模型類型進行特殊處理
    if model_class.__name__ == "CertifyToolMap":
        # CERTIFY_TOOL_MAP.csv 的欄位是 TOOL_ID，模型是 TOOL_ID（大小寫）
        if "TOOL_ID" in df.columns:
            column_mapping["TOOL_ID"] = "TOOL_ID"
    elif model_class.__name__ == "TrainingRecord":
        # TRAINING_RECORD.csv 的欄位
        if "Cer_type" in df.columns:
            column_mapping["Cer_type"] = "Cer_type"
    
    # 套用欄位名稱對映
    df = df.rename(columns=column_mapping)
    
    # 處理布林欄位
    boolean_fields = []
    for column in df.columns:
        # 檢查是否是布林欄位（根據名稱或內容）
        if 'Active' in column or column.startswith('Is'):
            boolean_fields.append(column)
    
    for field in boolean_fields:
        if field in df.columns:
            df[field] = df[field].apply(normalize_boolean)
    
    # 移除資料庫不存在的欄位
    model_columns = [col.name for col in model_class.__table__.columns]
    df = df[[col for col in df.columns if col in model_columns]]
    
    # 處理空字串
    df = df.replace({"": None, " ": None})
    
    return df

def migrate_table(csv_file, model_class, engine):
    """遷移單一資料表"""
    try:
        csv_path = DATA_DIR / csv_file
        if not csv_path.exists():
            logger.warning(f"CSV 檔案不存在: {csv_path}")
            return False
        
        # 讀取 CSV（處理編碼問題）
        try:
            df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 讀取失敗，嘗試 utf-8-sig: {csv_file}")
            df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, encoding='utf-8-sig')
        
        logger.info(f"正在處理 {csv_file}: {len(df)} 筆資料")
        
        # 清理資料
        df = clean_dataframe(df, model_class)
        
        # 分批寫入資料庫（避免記憶體問題）
        batch_size = 1000
        with Session(engine) as session:
            # 清空現有資料
            session.execute(text(f"DELETE FROM {model_class.__tablename__}"))
            session.commit()
            
            # 分批插入
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                records = batch.to_dict(orient='records')
                
                # 轉換為模型實例
                for record in records:
                    try:
                        obj = model_class(**record)
                        session.add(obj)
                    except Exception as e:
                        logger.error(f"建立物件失敗: {record}, 錯誤: {e}")
                        continue
                
                session.commit()
                logger.info(f"  已處理 {min(i+batch_size, len(df))}/{len(df)}")
        
        logger.info(f"✓ 成功遷移 {csv_file}: {len(df)} 筆資料")
        return True
        
    except Exception as e:
        logger.error(f"✗ 遷移失敗 {csv_file}: {e}")
        import traceback
        traceback.print_exc()
        return False

def migrate_data(engine):
    """執行完整遷移"""
    logger.info("=" * 60)
    logger.info("開始 CSV → SQLite 遷移")
    logger.info("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    # 依賴順序遷移（先對照表，再主檔，最後子檔）
    migration_order = [
        # 對照表（無外鍵依賴）
        ("L_Section.csv", Section),
        ("Area.csv", Area),
        ("L_Job.csv", Job),
        ("VAC_Type.csv", VacType),
        ("SHIFT.csv", Shift),
        ("SHOP.csv", Shop),
        ("CERTIFY_TYPE.csv", CertifyType),
        ("CERTIFY.csv", Certify),
        ("MUST_TOOL.csv", MustTool),  # 注意：全大寫
        ("SOFTWARE.csv", Software),
        
        # 主檔
        ("BASIC.csv", Basic),
        ("CERTIFY_ITEMS.csv", CertifyItem),
        
        # 子檔（有外鍵依賴）
        ("PERSON_INFO.csv", PersonInfo),
        ("TRAINING_RECORD.csv", TrainingRecord),
        ("CERTIFY_RECORD.csv", CertifyRecord),
        ("CERTIFY_TOOL_MAP.csv", CertifyToolMap),
        ("Authority.csv", Authority),
        ("DEL_AUTHORITY.csv", DelAuthority),
    ]
    
    for csv_file, model_class in migration_order:
        if migrate_table(csv_file, model_class, engine):
            success_count += 1
        else:
            fail_count += 1
    
    logger.info("=" * 60)
    logger.info(f"遷移完成！成功: {success_count}, 失敗: {fail_count}")
    logger.info("=" * 60)
    
    return success_count, fail_count

def verify_migration(engine):
    """驗證遷移結果"""
    logger.info("\n正在驗證遷移結果...")
    
    with Session(engine) as session:
        # 檢查各資料表筆數
        tables = [
            ("BASIC", Basic),
            ("L_Section", Section),
            ("Area", Area),
            ("PERSON_INFO", PersonInfo),
        ]
        
        for name, model in tables:
            count = session.query(model).count()
            logger.info(f"  {name}: {count} 筆資料")
    
    logger.info("✓ 驗證完成")

def main():
    """主函式"""
    # 建立資料庫引擎
    db_url = f"sqlite:///{SQLITE_PATH}"
    logger.info(f"建立資料庫: {SQLITE_PATH}")
    
    engine = create_engine(db_url, echo=False)
    
    # 1. 建立資料表結構
    logger.info("\n步驟 1: 建立資料表結構...")
    try:
        create_all_tables(engine)
        logger.info("✓ 資料表結構建立完成")
    except Exception as e:
        logger.error(f"✗ 建立資料表失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 2. 遷移資料
    logger.info("\n步驟 2: 開始遷移資料...")
    success, fail = migrate_data(engine)
    
    # 3. 驗證結果
    logger.info("\n步驟 3: 驗證遷移結果...")
    verify_migration(engine)
    
    logger.info(f"\n✓ 遷移完成！資料庫位置: {SQLITE_PATH}")
    
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
