#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRMS 最終整合測試腳本
測試應用程序啟動、UI模載入、Repository可用性和資料庫連接
"""

import sys
import os
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Any

# 添加專案根目錄到 sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

class IntegrationTestResult:
    """測試結果記錄"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_details: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        self.end_time = None
    
    def record_test(self, category: str, name: str, passed: bool, message: str = "", details: str = ""):
        """記錄測試結果"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        self.test_details.append({
            "category": category,
            "name": name,
            "passed": passed,
            "message": message,
            "details": details,
            "timestamp": datetime.now()
        })
    
    def finish(self):
        """完成測試"""
        self.end_time = datetime.now()
    
    @property
    def duration(self):
        """測試持續時間"""
        if self.end_time:
            return self.end_time - self.start_time
        return datetime.now() - self.start_time
    
    @property
    def pass_rate(self) -> float:
        """通過率"""
        if self.tests_run == 0:
            return 0.0
        return (self.tests_passed / self.tests_run) * 100

class HRMSIntegrationTest:
    """HRMS 整合測試類別"""
    
    def __init__(self):
        self.result = IntegrationTestResult()
        self.test_results: Dict[str, List[str]] = {}
    
    def test_environment_setup(self):
        """測試環境設定"""
        print("🧪 測試環境設定...")
        
        # 測試 Python 版本
        try:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            self.result.record_test(
                "環境", "Python 版本檢查", True,
                f"Python {python_version}",
                f"版本: {python_version}"
            )
        except Exception as e:
            self.result.record_test(
                "環境", "Python 版本檢查", False,
                f"檢查失敗: {str(e)}",
                traceback.format_exc()
            )
        
        # 測試專案根目錄
        try:
            self.result.record_test(
                "環境", "專案根目錄", True,
                f"專案根目錄: {PROJECT_ROOT}",
                f"路徑: {PROJECT_ROOT}"
            )
        except Exception as e:
            self.result.record_test(
                "環境", "專案根目錄", False,
                f"檢查失敗: {str(e)}",
                traceback.format_exc()
            )
        
        # 測試必要目錄
        required_dirs = [
            "hrms/ui/qt/windows",
            "hrms/ui/qt",
            "repositories",
            "hrms/core/db"
        ]
        
        for dir_path in required_dirs:
            full_path = os.path.join(PROJECT_ROOT, dir_path)
            try:
                exists = os.path.exists(full_path) and os.path.isdir(full_path)
                self.result.record_test(
                    "環境", f"目錄檢查: {dir_path}", exists,
                    f"{'存在' if exists else '不存在'}: {dir_path}",
                    f"完整路徑: {full_path}"
                )
            except Exception as e:
                self.result.record_test(
                    "環境", f"目錄檢查: {dir_path}", False,
                    f"檢查失敗: {str(e)}",
                    traceback.format_exc()
                )
    
    def test_database_connection(self):
        """測試資料庫連接"""
        print("🗄️ 測試資料庫連接...")
        
        try:
            from db import get_session, engine
            
            # 測試獲取 session
            session = get_session()
            self.result.record_test(
                "資料庫", "Session 建立", True,
                "成功建立資料庫 Session",
                f"Session 類型: {type(session).__name__}"
            )
            
            # 測試資料庫連接
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            self.result.record_test(
                "資料庫", "連接測試", True,
                "資料庫連接成功",
                f"Engine: {engine.url}"
            )
            
            # 測試資料庫檔案
            db_path = os.path.join(PROJECT_ROOT, "hrms.db")
            db_exists = os.path.exists(db_path)
            db_size = os.path.getsize(db_path) if db_exists else 0
            
            self.result.record_test(
                "資料庫", "資料庫檔案", db_exists,
                f"{'存在' if db_exists else '不存在'} (大小: {db_size} bytes)",
                f"路徑: {db_path}"
            )
            
            session.close()
            
        except Exception as e:
            self.result.record_test(
                "資料庫", "資料庫連接", False,
                f"連接失敗: {str(e)}",
                traceback.format_exc()
            )
    
    def test_imports(self):
        """測試所有模組導入"""
        print("📦 測試模組導入...")
        
        # PySide6 導入測試
        try:
            from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
            from PySide6.QtCore import Qt
            self.result.record_test(
                "導入", "PySide6 核心模組", True,
                "PySide6 核心模組導入成功",
                "包含: QtWidgets, QtCore"
            )
        except Exception as e:
            self.result.record_test(
                "導入", "PySide6 核心模組", False,
                f"導入失敗: {str(e)}",
                traceback.format_exc()
            )
        
        # 主應用程式導入測試
        try:
            from hrms.ui.qt.start_app import main as start_app_main
            self.result.record_test(
                "導入", "主應用程式模組", True,
                "主應用程式模組導入成功",
                "hrms.ui.qt.start_app"
            )
        except Exception as e:
            self.result.record_test(
                "導入", "主應用程式模組", False,
                f"導入失敗: {str(e)}",
                traceback.format_exc()
            )
    
    def test_ui_windows(self):
        """測試 UI 視窗模組（18個主要視窗）"""
        print("🪟 測試 UI 視窗模組...")
        
        # 定義 18 個主要視窗模組
        ui_windows = [
            # 主視窗
            ("hrms.ui.qt.windows.start_page_new", "StartPage"),
            
            # 基礎資料視窗
            ("hrms.ui.qt.windows.basic_window_new", "BasicWindow"),
            ("hrms.ui.qt.windows.dept_window_new", "DeptWindow"),
            ("hrms.ui.qt.windows.area_window_new", "AreaWindow"),
            ("hrms.ui.qt.windows.job_window_new", "JobWindow"),
            ("hrms.ui.qt.windows.shop_window_new", "ShopWindow"),
            ("hrms.ui.qt.windows.vac_type_window_new", "VacTypeWindow"),
            ("hrms.ui.qt.windows.shift_window_new", "ShiftWindow"),
            
            # 證照管理視窗
            ("hrms.ui.qt.windows.certify_management_window", "CertifyManagementWindow"),
            ("hrms.ui.qt.windows.certify_type_window_new", "CertifyTypeWindow"),
            ("hrms.ui.qt.windows.certify_window_new", "CertifyWindow"),
            ("hrms.ui.qt.windows.certify_items_window_new", "CertifyItemsWindow"),
            ("hrms.ui.qt.windows.certify_record_window_new", "CertifyRecordWindow"),
            ("hrms.ui.qt.windows.training_record_window_new", "TrainingRecordWindow"),
            
            # 權限管理視窗
            ("hrms.ui.qt.windows.authority_window", "AuthorityWindow"),
            ("hrms.ui.qt.windows.del_authority_window", "DelAuthorityWindow"),
            
            # 其他視窗
            ("hrms.ui.qt.windows.basic_csv_window", "BasicCSVWindow"),
            ("hrms.ui.qt.windows.certify_tool_map_window", "CertifyToolMapWindow"),
        ]
        
        imported_count = 0
        for module_path, class_name in ui_windows:
            try:
                module = __import__(module_path, fromlist=[class_name])
                window_class = getattr(module, class_name)
                self.result.record_test(
                    "UI視窗", f"{class_name}", True,
                    f"成功導入: {class_name}",
                    f"模組: {module_path}"
                )
                imported_count += 1
            except Exception as e:
                self.result.record_test(
                    "UI視窗", f"{class_name}", False,
                    f"導入失敗: {str(e)}",
                    f"模組: {module_path}\n{traceback.format_exc()}"
                )
        
        # 總結
        self.result.record_test(
            "UI視窗", f"UI視窗總計 ({imported_count}/{len(ui_windows)})", 
            imported_count == len(ui_windows),
            f"成功導入 {imported_count}/{len(ui_windows)} 個視窗",
            f"總計測試 {len(ui_windows)} 個視窗模組"
        )
    
    def test_repositories(self):
        """測試 Repository 可用性"""
        print("🗃️ 測試 Repository 可用性...")
        
        try:
            import repositories
            self.result.record_test(
                "Repository", "repositories 套件", True,
                "repositories 套件導入成功",
                f"套件路徑: {repositories.__file__}"
            )
        except Exception as e:
            self.result.record_test(
                "Repository", "repositories 套件", False,
                f"導入失敗: {str(e)}",
                traceback.format_exc()
            )
        
        # 測試個別 Repository
        repo_tests = [
            ("BaseRepository", "repositories.base", "BaseRepository"),
            ("ShopRepository", "repositories", "ShopRepository"),
            ("CertifyTypeRepository", "repositories", "CertifyTypeRepository"),
            ("CertifyRepository", "repositories", "CertifyRepository"),
            ("AreaRepository", "repositories", "AreaRepository"),
            ("DeptRepository", "repositories", "SectionRepository"),
            ("JobRepository", "repositories", "JobRepository"),
            ("LookupService", "repositories", "LookupService"),
            ("CertificationService", "repositories", "CertificationService"),
        ]
        
        for repo_name, module_path, class_name in repo_tests:
            try:
                module = __import__(module_path, fromlist=[class_name])
                repo_class = getattr(module, class_name)
                self.result.record_test(
                    "Repository", repo_name, True,
                    f"成功導入: {repo_name}",
                    f"模組: {module_path}"
                )
            except Exception as e:
                self.result.record_test(
                    "Repository", repo_name, False,
                    f"導入失敗: {str(e)}",
                    f"模組: {module_path}\n{traceback.format_exc()}"
                )
    
    def test_main_menu_buttons(self):
        """測試主選單按鈕功能（模擬測試）"""
        print("🖱️ 測試主選單按鈕功能...")
        
        # 這裡我們測試按鈕的 callback 是否存在
        button_tests = [
            ("基本資料管理", "_open_basic_window"),
            ("部門資料管理", "_open_dept_window"),
            ("工作區域管理", "_open_area_window"),
            ("職稱資料管理", "_open_job_window"),
            ("工站資料管理", "_open_shop_window"),
            ("證照管理系統", "_open_certify_window"),
            ("權限設定管理", "_open_authority_window"),
            ("假別資料管理", "_open_vac_type_window"),
            ("班別資料管理", "_open_shift_window"),
        ]
        
        try:
            from hrms.ui.qt.windows.start_page_new import StartPage
            
            # 檢查方法是否存在
            for btn_name, method_name in button_tests:
                try:
                    method = getattr(StartPage, method_name)
                    self.result.record_test(
                        "主選單", f"按鈕: {btn_name}", True,
                        f"按鈕 callback 存在: {method_name}",
                        f"方法: {method}"
                    )
                except AttributeError:
                    self.result.record_test(
                        "主選單", f"按鈕: {btn_name}", False,
                        f"按鈕 callback 不存在: {method_name}",
                        f"類別: StartPage"
                    )
        except Exception as e:
            self.result.record_test(
                "主選單", "主視窗載入", False,
                f"主視窗載入失敗: {str(e)}",
                traceback.format_exc()
            )
    
    def test_certify_management_window(self):
        """驗證證照管理主選單"""
        print("📋 驗證證照管理主選單...")
        
        try:
            from hrms.ui.qt.windows.certify_management_window import CertifyManagementWindow
            
            # 測試類別是否存在
            self.result.record_test(
                "證照管理", "主視窗類別", True,
                "CertifyManagementWindow 類別存在",
                f"類別: {CertifyManagementWindow}"
            )
            
            # 測試子視窗導入
            sub_windows = [
                ("certify_type_window_new", "CertifyTypeWindow"),
                ("certify_window_new", "CertifyWindow"),
                ("certify_items_window_new", "CertifyItemsWindow"),
                ("certify_record_window_new", "CertifyRecordWindow"),
                ("training_record_window_new", "TrainingRecordWindow"),
                ("certify_tool_map_window", "CertifyToolMapWindow"),
            ]
            
            for module_name, class_name in sub_windows:
                try:
                    module = __import__(f"hrms.ui.qt.windows.{module_name}", fromlist=[class_name])
                    window_class = getattr(module, class_name)
                    self.result.record_test(
                        "證照管理", f"子視窗: {class_name}", True,
                        f"成功導入: {class_name}",
                        f"模組: {module_name}"
                    )
                except Exception as e:
                    self.result.record_test(
                        "證照管理", f"子視窗: {class_name}", False,
                        f"導入失敗: {str(e)}",
                        traceback.format_exc()
                    )
            
        except Exception as e:
            self.result.record_test(
                "證照管理", "主視窗載入", False,
                f"載入失敗: {str(e)}",
                traceback.format_exc()
            )
    
    def test_shop_window(self):
        """驗證工站管理視窗"""
        print("🏭 驗證工站管理視窗...")
        
        try:
            from hrms.ui.qt.windows.shop_window_new import ShopWindow
            
            # 測試類別導入
            self.result.record_test(
                "工站管理", "視窗類別", True,
                "ShopWindow 類別存在",
                f"類別: {ShopWindow}"
            )
            
            # 測試 Repository
            try:
                from repositories import ShopRepository
                self.result.record_test(
                    "工站管理", "ShopRepository", True,
                    "ShopRepository 導入成功",
                    f"Repository: {ShopRepository}"
                )
            except Exception as e:
                self.result.record_test(
                    "工站管理", "ShopRepository", False,
                    f"導入失敗: {str(e)}",
                    traceback.format_exc()
                )
            
            # 測試資料模型
            try:
                from domain.models import Shop
                self.result.record_test(
                    "工站管理", "資料模型", True,
                    "Shop 資料模型存在",
                    f"模型: {Shop}"
                )
            except Exception as e:
                self.result.record_test(
                    "工站管理", "資料模型", False,
                    f"載入失敗: {str(e)}",
                    traceback.format_exc()
                )
            
            # 測試 UnitOfWork
            try:
                from hrms.core.db.unit_of_work_sqlite import UnitOfWork
                self.result.record_test(
                    "工站管理", "UnitOfWork", True,
                    "UnitOfWork 導入成功",
                    f"UnitOfWork: {UnitOfWork}"
                )
            except Exception as e:
                self.result.record_test(
                    "工站管理", "UnitOfWork", False,
                    f"導入失敗: {str(e)}",
                    traceback.format_exc()
                )
            
        except Exception as e:
            self.result.record_test(
                "工站管理", "視窗載入", False,
                f"載入失敗: {str(e)}",
                traceback.format_exc()
            )
    
    def generate_report(self) -> str:
        """生成測試報告"""
        self.result.finish()
        
        report = []
        report.append("# HRMS 最終整合測試報告")
        report.append("")
        report.append(f"**測試時間:** {self.result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**測試持續時間:** {self.result.duration.total_seconds():.2f} 秒")
        report.append(f"**總測試數:** {self.result.tests_run}")
        report.append(f"**通過數:** {self.result.tests_passed} ✅")
        report.append(f"**失敗數:** {self.result.tests_failed} ❌")
        report.append(f"**通過率:** {self.result.pass_rate:.1f}%")
        report.append("")
        
        # 按分類分組測試結果
        categories = {}
        for test in self.result.test_details:
            category = test["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(test)
        
        for category, tests in categories.items():
            report.append(f"## {category}")
            report.append("")
            
            # 計算該分類的統計
            category_total = len(tests)
            category_passed = len([t for t in tests if t["passed"]])
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            report.append(f"**通過率:** {category_passed}/{category_total} ({category_rate:.1f}%)")
            report.append("")
            
            for test in tests:
                status = "✅ 通過" if test["passed"] else "❌ 失敗"
                report.append(f"### {status} {test['name']}")
                report.append(f"**訊息:** {test['message']}")
                if test["details"]:
                    report.append(f"**詳情:**")
                    report.append(f"```")
                    report.append(test["details"])
                    report.append(f"```")
                report.append("")
        
        # 總結
        report.append("## 測試總結")
        report.append("")
        if self.result.tests_failed == 0:
            report.append("✅ **所有測試均通過！HRMS 應用程序已準備好啟動。**")
        else:
            report.append(f"⚠️ **發現 {self.result.tests_failed} 個失敗項目，請檢查錯誤訊息。**")
        report.append("")
        report.append("---")
        report.append("*此報告由最終整合測試腳本自動生成*")
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """執行所有測試"""
        print("=" * 60)
        print("HRMS 最終整合測試")
        print("=" * 60)
        print("")
        
        # 1. 環境設定測試
        self.test_environment_setup()
        print("")
        
        # 2. 資料庫連接測試
        self.test_database_connection()
        print("")
        
        # 3. 模組導入測試
        self.test_imports()
        print("")
        
        # 4. UI 視窗測試
        self.test_ui_windows()
        print("")
        
        # 5. Repository 測試
        self.test_repositories()
        print("")
        
        # 6. 主選單按鈕測試
        self.test_main_menu_buttons()
        print("")
        
        # 7. 證照管理主選單測試
        self.test_certify_management_window()
        print("")
        
        # 8. 工站管理視窗測試
        self.test_shop_window()
        print("")
        
        # 完成測試
        self.result.finish()
        
        # 生成報告
        report = self.generate_report()
        
        # 儲存報告
        report_path = os.path.join(PROJECT_ROOT, "FINAL_INTEGRATION_REPORT.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        # 顯示摘要
        print("=" * 60)
        print("測試完成！")
        print(f"總測試數: {self.result.tests_run}")
        print(f"通過數: {self.result.tests_passed} ✅")
        print(f"失敗數: {self.result.tests_failed} ❌")
        print(f"通過率: {self.result.pass_rate:.1f}%")
        print(f"測試持續時間: {self.result.duration.total_seconds():.2f} 秒")
        print("")
        print(f"詳細報告已儲存至: {report_path}")
        print("=" * 60)
        
        return self.result.tests_failed == 0

if __name__ == "__main__":
    test = HRMSIntegrationTest()
    success = test.run_all_tests()
    sys.exit(0 if success else 1)
