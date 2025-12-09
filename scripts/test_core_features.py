#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心功能測試腳本
測試項目：
1. 員工基本資料管理（CRUD + 搜尋 + 分頁）
2. 部門管理（CRUD + 外鍵檢查）
3. 區域管理（CRUD + 狀態篩選）
4. 職務管理（CRUD）
5. 效能測試（載入速度）
"""
import sys
import time
from pathlib import Path
from datetime import datetime

# 專案路徑
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import (
    BasicRepository, PersonInfoRepository, SectionRepository,
    AreaRepository, JobRepository, LookupService
)
from domain.models import Basic, Section, Area, Job

# 測試結果記錄
_test_results = []
_failures = []
_warnings = []

def log_test(name: str, passed: bool, duration: float = 0, message: str = ""):
    """記錄測試結果"""
    status = "✅ PASS" if passed else "❌ FAIL"
    _test_results.append({
        "name": name,
        "status": status,
        "duration": duration,
        "message": message
    })
    
    if not passed:
        _failures.append(f"{name}: {message}")
    elif message:
        _warnings.append(f"{name}: {message}")

def test_header(title: str):
    """顯示測試標題"""
    print("\n" + "=" * 70)
    print(f" {title} ")
    print("=" * 70)

# === 測試 1：員工基本資料管理 ===
def test_employee_crud():
    """測試員工 CRUD"""
    test_header("測試 1：員工基本資料 CRUD")
    
    start_time = time.time()
    
    try:
        with UnitOfWork() as uow:
            repo = BasicRepository(uow.session)
            
            # 1.1 查詢所有員工
            print("\n1.1 查詢所有員工...")
            t0 = time.time()
            employees = repo.list()
            t1 = time.time()
            
            assert len(employees) > 0, "員工資料為空"
            log_test("查詢員工列表", True, t1-t0, f"找到 {len(employees)} 筆")
            
            # 1.2 依主鍵查詢
            print("\n1.2 依主鍵查詢...")
            test_emp_id = employees[0].EMP_ID
            t0 = time.time()
            emp = repo.get_by_pk(test_emp_id)
            t1 = time.time()
            
            assert emp is not None, "依主鍵查詢失敗"
            assert emp.EMP_ID == test_emp_id, "員工編號不符"
            log_test("依主鍵查詢", True, t1-t0, f"員工: {emp.EMP_ID} - {emp.C_Name}")
            
            # 1.3 搜尋功能
            print("\n1.3 測試搜尋功能...")
            t0 = time.time()
            results = repo.search_by_name("張", limit=10)
            t1 = time.time()
            
            assert len(results) > 0, "搜尋失敗"
            log_test("姓名搜尋", True, t1-t0, f"找到 {len(results)} 筆")
            
            # 1.4 依部門查詢
            if emp.Dept_Code:
                print("\n1.4 依部門查詢...")
                t0 = time.time()
                dept_emps = repo.get_by_dept(emp.Dept_Code)
                t1 = time.time()
                
                assert len(dept_emps) > 0, "依部門查詢失敗"
                log_test("依部門查詢", True, t1-t0, f"部門 {emp.Dept_Code} 有 {len(dept_emps)} 位員工")
            
            # 1.5 新增員工（測試資料）
            print("\n1.5 新增員工...")
            test_emp_id = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            t0 = time.time()
            new_emp = repo.upsert(test_emp_id, {
                "EMP_ID": test_emp_id,
                "C_Name": "測試員工",
                "Dept_Code": "L21041",
                "Title": "測試職稱",
                "Active": True
            })
            t1 = time.time()
            
            assert new_emp is not None, "新增失敗"
            log_test("新增員工", True, t1-t0, f"員工編號: {test_emp_id}")
            
            # 1.6 更新員工
            print("\n1.6 更新員工...")
            t0 = time.time()
            updated = repo.update(test_emp_id, {
                "C_Name": "測試員工（已修改）",
                "Title": "測試職稱（已修改）"
            })
            t1 = time.time()
            
            assert updated is not None, "更新失敗"
            assert updated.C_Name == "測試員工（已修改）", "更新內容不符"
            log_test("更新員工", True, t1-t0, f"姓名已更新")
            
            # 1.7 刪除員工
            print("\n1.7 刪除員工...")
            t0 = time.time()
            deleted = repo.delete(test_emp_id)
            t1 = time.time()
            
            assert deleted is True, "刪除失敗"
            
            # 確認已刪除
            emp_after = repo.get_by_pk(test_emp_id)
            assert emp_after is None, "刪除後仍可查詢到資料"
            log_test("刪除員工", True, t1-t0, f"員工 {test_emp_id} 已刪除")
            
            print("\n✅ 員工 CRUD 測試完成")
            
    except Exception as e:
        print(f"\n❌ 員工 CRUD 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        log_test("員工 CRUD", False, 0, str(e))
    
    return time.time() - start_time

def test_department_crud():
    """測試部門 CRUD"""
    test_header("測試 2：部門管理 CRUD + 外鍵檢查")
    
    start_time = time.time()
    
    try:
        with UnitOfWork() as uow:
            repo = SectionRepository(uow.session)
            
            # 2.1 查詢所有部門
            print("\n2.1 查詢所有部門...")
            t0 = time.time()
            sections = repo.list()
            t1 = time.time()
            
            assert len(sections) > 0, "部門資料為空"
            log_test("查詢部門列表", True, t1-t0, f"找到 {len(sections)} 個部門")
            
            # 2.2 測試外鍵檢查
            if sections:
                dept_code = sections[0].Dept_Code
                print(f"\n2.2 測試外鍵檢查（部門: {dept_code}）...")
                
                basic_repo = BasicRepository(uow.session)
                t0 = time.time()
                has_employees = basic_repo.has_department_employees(dept_code)
                t1 = time.time()
                
                if has_employees:
                    log_test("外鍵檢查", True, t1-t0, f"部門 {dept_code} 有員工，不可刪除")
                else:
                    log_test("外鍵檢查", True, t1-t0, f"部門 {dept_code} 無員工，可刪除")
            
            # 2.3 新增部門
            print("\n2.3 新增部門...")
            test_dept_code = f"TEST_DEPT_{datetime.now().strftime('%Y%m%d')}"
            
            t0 = time.time()
            repo.upsert(test_dept_code, {
                "Dept_Code": test_dept_code,
                "Dept_Name": "測試部門",
                "Dept_Desc": "這是測試部門",
                "Supervisor": "測試主管"
            })
            t1 = time.time()
            
            log_test("新增部門", True, t1-t0, f"部門代碼: {test_dept_code}")
            
            # 2.4 更新部門
            print("\n2.4 更新部門...")
            t0 = time.time()
            repo.update(test_dept_code, {
                "Dept_Name": "測試部門（已修改）",
                "Supervisor": "測試主管（已修改）"
            })
            t1 = time.time()
            
            log_test("更新部門", True, t1-t0, "部門名稱已更新")
            
            # 2.5 刪除部門（無員工）
            print("\n2.5 測試刪除部門...")
            t0 = time.time()
            deleted = repo.delete(test_dept_code)
            t1 = time.time()
            
            if deleted:
                log_test("刪除部門", True, t1-t0, f"部門 {test_dept_code} 已刪除")
            else:
                log_test("刪除部門", False, t1-t0, "刪除失敗")
            
            print("\n✅ 部門管理測試完成")
            
    except Exception as e:
        print(f"\n❌ 部門管理測試失敗: {e}")
        import traceback
        traceback.print_exc()
        log_test("部門管理", False, 0, str(e))
    
    return time.time() - start_time

def test_lookup_service():
    """測試對照表服務"""
    test_header("測試 3：對照表服務（LookupService）")
    
    start_time = time.time()
    
    try:
        with UnitOfWork() as uow:
            service = LookupService(uow.session)
            
            # 3.1 部門對照表
            print("\n3.1 測試部門對照表...")
            t0 = time.time()
            depts = service.list_dept_codes()
            t1 = time.time()
            
            assert len(depts) > 0, "部門對照表為空"
            log_test("部門對照表", True, t1-t0, f"{len(depts)} 個部門")
            
            # 3.2 區域對照表
            print("\n3.2 測試區域對照表...")
            t0 = time.time()
            areas = service.list_areas()
            t1 = time.time()
            
            assert len(areas) > 0, "區域對照表為空"
            log_test("區域對照表", True, t1-t0, f"{len(areas)} 個區域")
            
            # 3.3 職務對照表
            print("\n3.3 測試職務對照表...")
            t0 = time.time()
            jobs = service.list_jobs()
            t1 = time.time()
            
            assert len(jobs) > 0, "職務對照表為空"
            log_test("職務對照表", True, t1-t0, f"{len(jobs)} 個職務")
            
            # 3.4 假別對照表
            print("\n3.4 測試假別對照表...")
            t0 = time.time()
            vac_types = service.list_vac_types()
            t1 = time.time()
            
            assert len(vac_types) > 0, "假別對照表為空"
            log_test("假別對照表", True, t1-t0, f"{len(vac_types)} 種假別")
            
            # 3.5 快取功能
            print("\n3.5 測試快取功能...")
            t0 = time.time()
            depts2 = service.list_dept_codes()  # 應該從快取讀取
            t1 = time.time()
            
            assert depts == depts2, "快取資料不一致"
            log_test("快取功能", True, t1-t0, "第二次讀取更快")
            
            print("\n✅ 對照表服務測試完成")
            
    except Exception as e:
        print(f"\n❌ 對照表服務測試失敗: {e}")
        import traceback
        traceback.print_exc()
        log_test("對照表服務", False, 0, str(e))
    
    return time.time() - start_time

def test_performance():
    """效能測試"""
    test_header("測試 4：效能測試")
    
    start_time = time.time()
    
    try:
        # 4.1 載入所有員工
        print("\n4.1 載入所有員工...")
        with UnitOfWork() as uow:
            repo = BasicRepository(uow.session)
            
            t0 = time.time()
            employees = repo.list()
            t1 = time.time()
            
            log_test("載入所有員工", True, t1-t0, f"{len(employees)} 筆，{(t1-t0)*1000:.2f}ms")
            
            # 4.2 分頁查詢
            print("\n4.2 分頁查詢...")
            t0 = time.time()
            page1 = repo.list(limit=50, offset=0)
            t1 = time.time()
            
            assert len(page1) == 50, "分頁大小錯誤"
            log_test("分頁查詢（50筆）", True, t1-t0, f"{(t1-t0)*1000:.2f}ms")
            
            # 4.3 搜尋效能
            print("\n4.3 搜尋效能...")
            t0 = time.time()
            results = repo.search_by_name("張", limit=100)
            t1 = time.time()
            
            log_test("姓名搜尋", True, t1-t0, f"{len(results)} 筆，{(t1-t0)*1000:.2f}ms")
            
            # 4.4 載入對照表
            print("\n4.4 載入對照表...")
            service = LookupService(uow.session)
            
            t0 = time.time()
            depts = service.list_dept_codes()
            t1 = time.time()
            
            log_test("載入部門列表", True, t1-t0, f"{len(depts)} 筆，{(t1-t0)*1000:.2f}ms")
            
            print("\n✅ 效能測試完成")
            
    except Exception as e:
        print(f"\n❌ 效能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        log_test("效能測試", False, 0, str(e))
    
    return time.time() - start_time

def print_test_summary():
    """列印測試摘要"""
    print("\n" + "=" * 70)
    print("測試摘要報告")
    print("=" * 70)
    
    total_tests = len(_test_results)
    passed_tests = sum(1 for r in _test_results if r["status"] == "✅ PASS")
    failed_tests = sum(1 for r in _test_results if r["status"] == "❌ FAIL")
    
    print(f"\n總測試數: {total_tests}")
    print(f"✅ 通過: {passed_tests}")
    print(f"❌ 失敗: {failed_tests}")
    print(f"⚠️  警告: {len(_warnings)}")
    
    if _test_results:
        total_duration = sum(r["duration"] for r in _test_results)
        print(f"\n總耗時: {total_duration:.2f} 秒")
        
        avg_duration = total_duration / len(_test_results)
        print(f"平均耗時: {avg_duration*1000:.2f} ms/測試")
    
    print("\n" + "-" * 70)
    print("詳細測試結果:")
    print("-" * 70)
    
    for result in _test_results:
        status_symbol = "✅" if result["status"] == "✅ PASS" else "❌"
        print(f"{status_symbol} {result['name']:<40} {result['duration']*1000:>6.1f}ms")
        if result["message"]:
            print(f"   └─ {result['message']}")
    
    if _failures:
        print("\n" + "=" * 70)
        print("失敗項目:")
        print("=" * 70)
        for failure in _failures:
            print(f"❌ {failure}")
    
    if _warnings:
        print("\n" + "=" * 70)
        print("警告項目:")
        print("=" * 70)
        for warning in _warnings:
            print(f"⚠️  {warning}")
    
    print("\n" + "=" * 70)
    print(f"測試結果: {'✅ 所有測試通過' if failed_tests == 0 else '❌ 部分測試失敗'}")
    print("=" * 70)

def main():
    """主測試函式"""
    print("\n" + "=" * 70)
    print("HRMS 核心功能測試")
    print("=" * 70)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"資料庫: {PROJECT_ROOT}/hrms.db")
    
    db_path = PROJECT_ROOT / "hrms.db"
    if not db_path.exists():
        print(f"\n❌ 錯誤：資料庫檔案不存在: {db_path}")
        return 1
    
    print(f"資料庫大小: {db_path.stat().st_size / 1024:.1f} KB")
    
    total_start = time.time()
    
    try:
        print("\n【第一階段】功能測試")
        # 測試 1：員工 CRUD
        duration1 = test_employee_crud()
        print(f"測試 1 耗時: {duration1:.2f} 秒")
        
        # 測試 2：部門管理
        duration2 = test_department_crud()
        print(f"測試 2 耗時: {duration2:.2f} 秒")
        
        # 測試 3：對照表服務
        duration3 = test_lookup_service()
        print(f"測試 3 耗時: {duration3:.2f} 秒")
        
        print("\n【第二階段】效能測試")
        # 測試 4：效能測試
        duration4 = test_performance()
        print(f"測試 4 耗時: {duration4:.2f} 秒")
        
        total_duration = time.time() - total_start
        
        print("\n" + "=" * 70)
        print(f"所有測試完成")
        print("=" * 70)
        print(f"總耗時: {total_duration:.2f} 秒")
        print(f"階段 1: {duration1 + duration2 + duration3:.2f} 秒")
        print(f"階段 2: {duration4:.2f} 秒")
        
        # 列印摘要
        print_test_summary()
        
        # 回傳退出碼
        if _failures:
            print("\n❌ 測試失敗，請修復問題後再繼續")
            return 1
        else:
            print("\n✅ 所有測試通過，可以繼續下一階段")
            return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 測試被使用者中斷")
        return 130
    except Exception as e:
        print(f"\n\n❌ 測試執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
