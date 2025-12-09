#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRMS 數據庫連接測試
測試數據庫連接、讀取和核心功能
"""

import os
import sys
from pathlib import Path

# 設定環境
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_database_connection():
    """測試數據庫連接"""
    print("=" * 80)
    print("HRMS 資料庫連接測試")
    print("=" * 80)
    print()
    
    try:
        import db
        print("【資料庫模組導入】")
        print("  ✓ db 模組導入成功")
        
        print()
        print("【資料庫連接測試】")
        
        # 獲取數據庫 URL
        from config import settings
        print(f"  資料庫 URL: {settings.db_url}")
        
        # 測試連接
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  ✓ 連接測試成功")
        
        print()
        print("【資料庫表格檢查】")
        
        # 檢查表格
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"  資料庫中共有 {len(tables)} 個表格")
        
        # 列出所有表格
        for table in sorted(tables):
            try:
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"    - {table:30s} ({count:5d} 筆記錄)")
            except:
                print(f"    - {table:30s} (無法讀取筆數)")
        
        print()
        
        if tables:
            print("✓ 資料庫連接和讀取成功")
            return True
        else:
            print("⚠ 資料庫連接成功但無表格")
            return False
        
    except Exception as e:
        print()
        print(f"✗ 資料庫測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_orm_functionality():
    """測試 ORM 功能"""
    print()
    print("=" * 80)
    print("HRMS ORM 功能測試")
    print("=" * 80)
    print()
    
    try:
        print("【資料庫會話測試】")
        
        # 測試會話
        from db import get_db_session
        from config import settings
        
        with get_db_session() as session:
            print("  ✓ 資料庫會話創建成功")
            print(f"  ✓ 資料庫 URL: {settings.db_url}")
            
            # 測試查詢
            result = session.execute("SELECT 1").scalar()
            print(f"  ✓ 簡單查詢測試成功 (結果: {result})")
        
        print()
        
        # 測試主要的 repository
        repositories = [
            ("repositories.basic_repository", "BasicRepository"),
            ("repositories.department_repository", "DepartmentRepository"),
            ("repositories.area_repository", "AreaRepository"),
            ("repositories.job_repository", "JobRepository"),
            ("repositories.certification_repository", "CertificationRepository"),
        ]
        
        print("【Repository 模組測試】")
        success_count = 0
        total_count = len(repositories)
        
        for module_name, class_name in repositories:
            try:
                module = __import__(module_name, fromlist=[class_name])
                print(f"  ✓ {class_name:35s} - 導入成功")
                success_count += 1
            except Exception as e:
                print(f"  ⚠ {class_name:35s} - 導入失敗: {str(e)[:40]}")
        
        print()
        
        if success_count == total_count:
            print(f"✓ 所有 Repository 模組成功 ({success_count}/{total_count})")
            return True
        else:
            print(f"⚠ 部分 Repository 模組失敗 ({success_count}/{total_count})")
            return False
        
    except Exception as e:
        print()
        print(f"✗ ORM 功能測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config_settings():
    """測試配置設定"""
    print()
    print("=" * 80)
    print("HRMS 設定測試")
    print("=" * 80)
    print()
    
    try:
        print("【設定檔案載入】")
        
        from config import settings
        print(f"  應用程式名稱: {settings.app_name}")
        print(f"  資料庫URL: {settings.db_url}")
        
        print()
        
        # 環境變量
        print("【環境變量測試】")
        env_vars = {
            'APP_NAME': os.environ.get('APP_NAME', '未設定'),
            'DB_URL': os.environ.get('DB_URL', '未設定'),
            'DEBUG': os.environ.get('DEBUG', '未設定'),
        }
        
        for key, value in env_vars.items():
            if value != '未設定':
                print(f"  ✓ {key:20s} = {value}")
            else:
                print(f"  ⚠ {key:20s} = {value}")
        
        print()
        print("✓ 設定測試成功")
        return True
        
    except Exception as e:
        print()
        print(f"✗ 設定測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("HRMS 資料庫與設定測試")
    print()
    
    try:
        all_passed = True
        
        # 測試設定
        if not test_config_settings():
            all_passed = False
        
        # 測試資料庫連接
        if not test_database_connection():
            all_passed = False
        
        # 測試 ORM 功能
        if not test_orm_functionality():
            all_passed = False
        
        print()
        print("=" * 80)
        print("最終結果:")
        if all_passed:
            print("✓ 所有資料庫和設定測試通過")
            sys.exit(0)
        else:
            print("✗ 部分測試失敗")
            sys.exit(1)
            
    except Exception as e:
        print(f"測試執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)