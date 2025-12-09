#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
證照管理基本測試
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import TrainingRecordRepository, CertifyItemRepository

def test_training_record_repository():
    """測試 TrainingRecordRepository"""
    print("\n=== 測試證照記錄 Repository ===\n")
    
    with UnitOfWork() as uow:
        repo = TrainingRecordRepository(uow.session)
        
        # 測試 1：計算總筆數
        print("1. 計算總筆數...")
        count = repo.count()
        print(f"   總筆數: {count}")
        assert count > 0, "證照記錄不應為空"
        
        # 測試 2：分頁查詢
        print("2. 分頁查詢（前 10 筆）...")
        records = repo.list(limit=10)
        print(f"   查詢到 {len(records)} 筆")
        for i, rec in enumerate(records, 1):
            print(f"   {i}. {rec.Certify_No}: {rec.EMP_ID} - {rec.Certify_ID}")
        
        # 測試 3：依員工查詢
        print("\n3. 依員工查詢（000490）...")
        emp_records = repo.get_by_employee("000490")
        print(f"   員工 000490 有 {len(emp_records)} 筆證照記錄")
        
        # 測試 4：依證照查詢
        print("\n4. 依證照查詢（MFG-I-011）...")
        certify_records = repo.get_by_certify_item("MFG-I-011")
        print(f"   證照 MFG-I-011 有 {len(certify_records)} 筆記錄")
        
        print("\n✅ 證照記錄 Repository 測試通過")

def test_certify_item_repository():
    """測試 CertifyItemRepository"""
    print("\n=== 測試證照項目 Repository ===\n")
    
    with UnitOfWork() as uow:
        repo = CertifyItemRepository(uow.session)
        
        print("1. 計算總筆數...")
        count = repo.count()
        print(f"   總筆數: {count}")
        assert count > 0, "證照項目不應為空"
        
        print("\n2. 查詢前 5 個證照項目...")
        items = repo.list(limit=5)
        for i, item in enumerate(items, 1):
            print(f"   {i}. {item.Certify_ID}: {item.Certify_Name} ({item.Certify_Type})")
        
        print("\n3. 依部門查詢（EPI）...")
        dept_items = repo.get_by_dept("EPI")
        print(f"   部門 EPI 有 {len(dept_items)} 個證照項目")
        
        print("\n✅ 證照項目 Repository 測試通過")

if __name__ == "__main__":
    print("=" * 60)
    print("證照管理基本測試")
    print("=" * 60)
    
    try:
        test_training_record_repository()
        test_certify_item_repository()
        
        print("\n" + "=" * 60)
        print("✅ 所有證照管理測試通過！")
        print("=" * 60)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
