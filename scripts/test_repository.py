#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Repository 層
驗證所有 Repository 基本功能
"""
import sys
from pathlib import Path

# 專案路徑
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import *
from domain.models import Basic

def test_basic_repository():
    """測試 BasicRepository"""
    print("\n" + "=" * 60)
    print("測試 BasicRepository")
    print("=" * 60)
    
    with UnitOfWork() as uow:
        repo = BasicRepository(uow.session)
        
        # 測試 count
        count = repo.count()
        print(f"✓ 資料筆數: {count}")
        
        # 測試 list（分頁）
        employees = repo.list(limit=5)
        print(f"✓ 查詢前 5 筆: 成功 ({len(employees)} 筆)")
        
        for emp in employees:
            print(f"  - {emp.EMP_ID}: {emp.C_Name}")
        
        # 測試 get_by_pk
        if employees:
            emp_id = employees[0].EMP_ID
            emp = repo.get_by_pk(emp_id)
            print(f"✓ 依主鍵查詢: {emp_id} → {emp.C_Name if emp else 'Not Found'}")
        
        # 測試搜尋
        results = repo.search_by_name("張", limit=3)
        print(f"✓ 姓名搜尋 '張': 找到 {len(results)} 筆")
        
        # 測試依部門查詢
        if employees and employees[0].Dept_Code:
            dept_code = employees[0].Dept_Code
            dept_emps = repo.get_by_dept(dept_code, only_active=True)
            print(f"✓ 依部門查詢 '{dept_code}': {len(dept_emps)} 筆在職員工")
        
        print("\n✓ BasicRepository 測試完成！")

def test_lookup_service():
    """測試 LookupService"""
    print("\n" + "=" * 60)
    print("測試 LookupService")
    print("=" * 60)
    
    with UnitOfWork() as uow:
        service = LookupService(uow.session)
        
        # 測試部門
        depts = service.list_dept_codes()
        print(f"✓ 部門代碼: {len(depts)} 個")
        print(f"  範例: {depts[:3]}")
        
        # 測試區域
        areas = service.list_areas()
        print(f"✓ 區域: {len(areas)} 個")
        print(f"  範例: {areas[:3]}")
        
        # 測試職務
        jobs = service.list_jobs()
        print(f"✓ 職務: {len(jobs)} 個")
        print(f"  範例: {jobs[:3]}")
        
        # 測試假別
        vac_types = service.list_vac_types()
        print(f"✓ 假別: {len(vac_types)} 個")
        
        # 測試班別
        shifts = service.list_shifts()
        print(f"✓ 班別: {len(shifts)} 個")
        
        # 測試工站
        shops = service.list_shop_codes()
        print(f"✓ 工站: {len(shops)} 個")
        
        print("\n✓ LookupService 測試完成！")

def test_certification_repository():
    """測試證照相關 Repository"""
    print("\n" + "=" * 60)
    print("測試 Certification Repository")
    print("=" * 60)
    
    with UnitOfWork() as uow:
        # 測試 CertifyItemRepository
        item_repo = CertifyItemRepository(uow.session)
        items = item_repo.list(limit=3)
        print(f"✓ 證照項目: {item_repo.count()} 筆")
        if items:
            print(f"  範例: {items[0].Certify_ID} - {items[0].Certify_Name}")
        
        # 測試 TrainingRecordRepository
        record_repo = TrainingRecordRepository(uow.session)
        count = record_repo.count()
        print(f"✓ 證照記錄: {count} 筆")
        
        first_5 = record_repo.list(limit=5)
        for record in first_5:
            print(f"  - {record.Certify_No}: {record.EMP_ID} → {record.Certify_ID}")
        
        print("\n✓ Certification Repository 測試完成！")

def test_authority_repository():
    """測試權限 Repository"""
    print("\n" + "=" * 60)
    print("測試 Authority Repository")
    print("=" * 60)
    
    with UnitOfWork() as uow:
        # 測試 AuthorityRepository
        auth_repo = AuthorityRepository(uow.session)
        users = auth_repo.get_active_users()
        print(f"✓ 有效使用者: {len(users)} 位")
        
        for user in users[:3]:
            print(f"  - {user.S_Account}: Auth_type={user.Auth_type}")
        
        # 測試權限檢查
        if users:
            test_account = users[0].S_Account
            # 建立 DelAuthorityRepository
            del_auth_repo = DelAuthorityRepository(uow.session)
            can_delete = del_auth_repo.has_delete_permission(test_account)
            print(f"\n✓ 帳號 '{test_account}' 刪除權限: {can_delete}")
        
        # 測試 AuthorizationService
        auth_service = AuthorizationService(uow.session)
        if users:
            test_account = users[0].S_Account
            result = auth_service.login(test_account)
            if result["success"]:
                print(f"✓ 登入測試成功: {result['user']['account']}")
            else:
                print(f"⚠ 登入測試失敗: {result['message']}")
        
        print("\n✓ Authority Repository 測試完成！")

def test_upsert():
    """測試 Upsert 功能"""
    print("\n" + "=" * 60)
    print("測試 Upsert 功能")
    print("=" * 60)
    
    with UnitOfWork() as uow:
        repo = BasicRepository(uow.session)
        
        # 測試更新（該員工應該存在）
        test_emp_id = "000056"
        
        # 先查詢現有資料
        emp_before = repo.get_by_pk(test_emp_id)
        if emp_before:
            print(f"\n員工 {test_emp_id} 修改前:")
            print(f"  姓名: {emp_before.C_Name}")
            print(f"  部門: {emp_before.Dept_Code}")
            print(f"  狀態: {emp_before.Active}")
            
            # 測試更新（不改變實際資料，只是測試功能）
            result = repo.upsert(test_emp_id, {
                "EMP_ID": test_emp_id,
                "C_Name": emp_before.C_Name,
                "Dept_Code": emp_before.Dept_Code,
                "Active": emp_before.Active
            })
            
            print(f"\n✓ Upsert 成功: {result.C_Name}")
        else:
            print(f"⚠ 測試員工 {test_emp_id} 不存在，跳過此測試")
        
        print("\n✓ Upsert 測試完成！")

def main():
    """主測試函式"""
    print("\n" + "=" * 60)
    print("Repository 層測試")
    print("=" * 60)
    print(f"資料庫: {PROJECT_ROOT}/hrms.db")
    
    # 檢查資料庫是否存在
    db_path = PROJECT_ROOT / "hrms.db"
    if not db_path.exists():
        print(f"✗ 錯誤：資料庫檔案不存在: {db_path}")
        return 1
    
    print(f"資料庫大小: {db_path.stat().st_size / 1024:.1f} KB")
    
    try:
        # 執行測試
        test_basic_repository()
        test_lookup_service()
        test_certification_repository()
        test_authority_repository()
        test_upsert()
        
        print("\n" + "=" * 60)
        print("✅ 所有測試完成！")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
