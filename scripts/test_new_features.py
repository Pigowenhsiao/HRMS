#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新功能測試腳本
測試證照管理和工站管理功能
"""

import sys
import os
import traceback
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# 測試報告存儲路徑
REPORT_PATH = Path(__file__).parent / "new_features_test_report.txt"

class TestReport:
    """測試報告生成器"""
    
    def __init__(self):
        self.tests = []
        self.start_time = datetime.now()
        
    def add_test(self, name, status, message="", error_details=""):
        """添加測試結果"""
        self.tests.append({
            "name": name,
            "status": status,  # PASS, FAIL, WARNING
            "message": message,
            "error_details": error_details,
            "timestamp": datetime.now()
        })
    
    def generate_report(self):
        """生成測試報告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = []
        report.append("=" * 80)
        report.append("新功能測試報告")
        report.append("=" * 80)
        report.append(f"測試時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"總耗時: {duration.total_seconds():.2f} 秒")
        report.append("=" * 80)
        report.append("")
        
        # 統計結果
        total = len(self.tests)
        passed = len([t for t in self.tests if t["status"] == "PASS"])
        failed = len([t for t in self.tests if t["status"] == "FAIL"])
        warnings = len([t for t in self.tests if t["status"] == "WARNING"])
        
        report.append("測試結果統計:")
        report.append(f"  總測試數: {total}")
        report.append(f"  通過: {passed}")
        report.append(f"  失敗: {failed}")
        report.append(f"  警告: {warnings}")
        report.append("")
        
        if failed > 0:
            report.append("❌ 測試結果: 部分失敗")
        elif warnings > 0:
            report.append("⚠️ 測試結果: 存在警告")
        else:
            report.append("✅ 測試結果: 全部通過")
        report.append("")
        
        # 詳細測試結果
        report.append("詳細測試結果:")
        report.append("-" * 80)
        
        for i, test in enumerate(self.tests, 1):
            status_icon = "✅" if test["status"] == "PASS" else "❌" if test["status"] == "FAIL" else "⚠️"
            report.append(f"{i:2d}. [{status_icon}] {test['name']}")
            if test["message"]:
                report.append(f"     訊息: {test['message']}")
            if test["error_details"]:
                report.append(f"     錯誤詳情:\n{test['error_details']}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self):
        """保存報告到文件"""
        report_content = self.generate_report()
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"測試報告已保存到: {REPORT_PATH}")

def test_import(module_path, class_name=None):
    """測試導入模塊"""
    try:
        parts = module_path.split(".")
        module = __import__(module_path, fromlist=[parts[-1]])
        if class_name:
            cls = getattr(module, class_name)
            return True, f"成功導入 {module_path}.{class_name}", None
        return True, f"成功導入 {module_path}", None
    except Exception as e:
        error_details = traceback.format_exc()
        return False, f"導入失敗: {str(e)}", error_details

def test_window_class(module_path, class_name):
    """測試窗口類的基本結構（不創建實例）"""
    try:
        parts = module_path.split(".")
        module = __import__(module_path, fromlist=[parts[-1]])
        cls = getattr(module, class_name)
        
        # 檢查類的基本信息
        info = []
        info.append(f"類名: {cls.__name__}")
        info.append(f"模塊: {cls.__module__}")
        
        # 檢查 __init__ 方法
        if hasattr(cls, '__init__'):
            info.append("✓ 含有 __init__ 方法")
        
        # 檢查父類
        bases = cls.__bases__
        if bases:
            base_names = [b.__name__ for b in bases]
            info.append(f"父類: {', '.join(base_names)}")
        
        return True, "; ".join(info), None
    except Exception as e:
        error_details = traceback.format_exc()
        return False, f"測試失敗: {str(e)}", error_details

def main():
    """主測試函數"""
    print("開始測試新開發的證照管理和工站管理功能...")
    report = TestReport()
    
    # 測試 1: 測試核心依賴
    print("\n1. 測試核心依賴...")
    
    # 測試 models
    status, msg, error = test_import("domain.models.certification")
    report.add_test("導入 domain.models.certification", 
                    "PASS" if status else "FAIL", msg, error)
    
    # 測試 repositories
    status, msg, error = test_import("repositories.certification")
    report.add_test("導入 repositories.certification", 
                    "PASS" if status else "FAIL", msg, error)
    
    # 測試 UnitOfWork
    status, msg, error = test_import("hrms.core.db.unit_of_work_sqlite", "UnitOfWork")
    report.add_test("導入 UnitOfWork", 
                    "PASS" if status else "FAIL", msg, error)
    
    # 測試 basic_csv_window
    status, msg, error = test_import("hrms.ui.qt.windows.basic_csv_window", "BasicCSVWindow")
    report.add_test("導入 BasicCSVWindow", 
                    "PASS" if status else "FAIL", msg, error)
    
    # 測試 2: ShopWindow (工站管理)
    print("\n2. 測試 ShopWindow (工站管理)...")
    
    status, msg, error = test_import("hrms.ui.qt.windows.shop_window", "ShopWindow")
    report.add_test("導入 ShopWindow", 
                    "PASS" if status else "FAIL", msg, error)
    
    if status:
        # 測試類結構
        status, msg, error = test_window_class("hrms.ui.qt.windows.shop_window", "ShopWindow")
        report.add_test("ShopWindow 類結構", 
                        "PASS" if status else "FAIL", msg, error)
    
    # 測試 3: CertifyManagementWindow (證照管理主選單)
    print("\n3. 測試 CertifyManagementWindow (證照管理主選單)...")
    
    status, msg, error = test_import("hrms.ui.qt.windows.certify_management_window", "CertifyManagementWindow")
    report.add_test("導入 CertifyManagementWindow", 
                    "PASS" if status else "FAIL", msg, error)
    
    if status:
        status, msg, error = test_window_class("hrms.ui.qt.windows.certify_management_window", "CertifyManagementWindow")
        report.add_test("CertifyManagementWindow 類結構", 
                        "PASS" if status else "FAIL", msg, error)
    
    # 測試相關的視窗
    related_windows = [
        ("hrms.ui.qt.windows.certify_type_window_new", "CertifyTypeWindow"),
        ("hrms.ui.qt.windows.certify_window_new", "CertifyWindow"),
        ("hrms.ui.qt.windows.certify_items_window_new", "CertifyItemsWindow"),
        ("hrms.ui.qt.windows.certify_record_window_new", "CertifyRecordWindow"),
        ("hrms.ui.qt.windows.certify_tool_map_window", "CertifyToolMapWindow"),
    ]
    
    for module_path, class_name in related_windows:
        short_name = class_name.replace("Window", "")
        status, msg, error = test_import(module_path, class_name)
        status_level = "PASS" if status else "WARNING" if "training" in module_path.lower() else "FAIL"
        report.add_test(f"導入 {short_name}", status_level, msg, error)
        
        if status:
            status2, msg2, error2 = test_window_class(module_path, class_name)
            report.add_test(f"{short_name} 類結構", 
                            "PASS" if status2 else "WARNING", msg2, error2)
    
    # 測試 4: CertifyTypeWindow (認證類型管理)
    print("\n4. 測試 CertifyTypeWindow (認證類型管理)...")
    
    status, msg, error = test_import("hrms.ui.qt.windows.certify_type_window_new", "CertifyTypeWindow")
    report.add_test("導入 CertifyTypeWindow (SQLite)", 
                    "PASS" if status else "FAIL", msg, error)
    
    if status:
        status, msg, error = test_window_class("hrms.ui.qt.windows.certify_type_window_new", "CertifyTypeWindow")
        report.add_test("CertifyTypeWindow (SQLite) 類結構", 
                        "PASS" if status else "FAIL", msg, error)
    
    # 測試 5: CertifyWindow (認證總表管理)
    print("\n5. 測試 CertifyWindow (認證總表管理)...")
    
    status, msg, error = test_import("hrms.ui.qt.windows.certify_window_new", "CertifyWindow")
    report.add_test("導入 CertifyWindow (SQLite)", 
                    "PASS" if status else "FAIL", msg, error)
    
    if status:
        status, msg, error = test_window_class("hrms.ui.qt.windows.certify_window_new", "CertifyWindow")
        report.add_test("CertifyWindow (SQLite) 類結構", 
                        "PASS" if status else "FAIL", msg, error)
    
    # 測試 6: 測試數據庫連接
    print("\n6. 測試數據庫連接...")
    
    try:
        from hrms.core.db.unit_of_work_sqlite import UnitOfWork
        from sqlalchemy import text
        with UnitOfWork() as uow:
            # 測試基本查詢
            session = uow.session
            result = session.execute(text("SELECT 1")).scalar()
            if result == 1:
                report.add_test("SQLite 數據庫連接", "PASS", "成功連接到數據庫")
            else:
                report.add_test("SQLite 數據庫連接", "FAIL", "數據庫連接測試失敗")
    except Exception as e:
        error_details = traceback.format_exc()
        report.add_test("SQLite 數據庫連接", "FAIL", 
                      f"連接失敗: {str(e)}", error_details)
    
    # 測試 7: 檢查必要的數據結構
    print("\n7. 檢查必要的數據結構...")
    
    try:
        from hrms.core.db.unit_of_work_sqlite import UnitOfWork
        from domain.models import Certify, CertifyType, CertifyItem
        
        with UnitOfWork() as uow:
            session = uow.session
            # 檢查 CERTIFY 表
            try:
                count = session.query(Certify).count()
                report.add_test("CERTIFY 數據表", "PASS", f"表存在, 記錄數: {count}")
            except Exception as e:
                report.add_test("CERTIFY 數據表", "WARNING", 
                              f"表可能不存在或無法訪問: {str(e)}")
            
            # 檢查 CERTIFY_TYPE 表
            try:
                count = session.query(CertifyType).count()
                report.add_test("CERTIFY_TYPE 數據表", "PASS", f"表存在, 記錄數: {count}")
            except Exception as e:
                report.add_test("CERTIFY_TYPE 數據表", "WARNING", 
                              f"表可能不存在或無法訪問: {str(e)}")
            
            # 檢查 CERTIFY_ITEMS 表
            try:
                count = session.query(CertifyItem).count()
                report.add_test("CERTIFY_ITEMS 數據表", "PASS", f"表存在, 記錄數: {count}")
            except Exception as e:
                report.add_test("CERTIFY_ITEMS 數據表", "WARNING", 
                              f"表可能不存在或無法訪問: {str(e)}")
    except Exception as e:
        error_details = traceback.format_exc()
        report.add_test("數據結構檢查", "FAIL", 
                      f"檢查失敗: {str(e)}", error_details)
    
    # 測試 8: 測試 Repository 功能
    print("\n8. 測試 Repository 功能...")
    
    try:
        from hrms.core.db.unit_of_work_sqlite import UnitOfWork
        from repositories import CertifyTypeRepository, CertifyRepository
        
        with UnitOfWork() as uow:
            # 測試 CertifyTypeRepository
            try:
                repo = CertifyTypeRepository(uow.session)
                report.add_test("CertifyTypeRepository", "PASS", "成功創建 Repository 實例")
            except Exception as e:
                report.add_test("CertifyTypeRepository", "FAIL", f"創建失敗: {str(e)}")
            
            # 測試 CertifyRepository
            try:
                repo = CertifyRepository(uow.session)
                report.add_test("CertifyRepository", "PASS", "成功創建 Repository 實例")
            except Exception as e:
                report.add_test("CertifyRepository", "FAIL", f"創建失敗: {str(e)}")
    except Exception as e:
        error_details = traceback.format_exc()
        report.add_test("Repository 功能測試", "FAIL", 
                      f"測試失敗: {str(e)}", error_details)
    
    # 生成並保存報告
    print("\n生成測試報告...")
    report.save_report()
    
    # 打印總結
    summary = report.generate_report()
    print("\n" + "=" * 80)
    print("測試摘要:")
    print("=" * 80)
    
    total = len(report.tests)
    passed = len([t for t in report.tests if t["status"] == "PASS"])
    failed = len([t for t in report.tests if t["status"] == "FAIL"])
    warnings = len([t for t in report.tests if t["status"] == "WARNING"])
    
    print(f"總測試數: {total}")
    print(f"通過: {passed}")
    print(f"失敗: {failed}")
    print(f"警告: {warnings}")
    
    if failed > 0:
        print("\n❌ 測試結果: 部分失敗")
        sys.exit(1)
    elif warnings > 0:
        print("\n⚠️ 測試結果: 存在警告")
        sys.exit(0)
    else:
        print("\n✅ 測試結果: 全部通過")
        sys.exit(0)

if __name__ == "__main__":
    main()
