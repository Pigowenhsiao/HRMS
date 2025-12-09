#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRMS 最終完整測試報告生成器
測試所有 12 個主要功能模組並生成完整的 Markdown 格式測試報告

功能模組列表 (共 12 個):
1. 員工基本資料管理 (basic_window_new)
2. 部門管理 (dept_window_new)
3. 區域管理 (area_window_new)
4. 職務管理 (job_window_new)
5. 班別管理 (shift_window_new)
6. 證照項目管理 (certify_items_window_new)
7. 證照記錄管理 (certify_record_window_new)
8. 訓練記錄管理 (training_record_window_new)
9. 假別管理 (vac_type_window_new)
10. 權限管理 (authority_window_new)
11. 店鋪管理 (shop_window_new)
12. 系統主頁面 (start_page_new)
"""

import os
import sys
import time
import platform
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 設定環境
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

class HRMSFinalTester:
    """HRMS 最終完整測試器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = Path(__file__).parent
        self.report_file = self.scripts_dir / "FINAL_TEST_REPORT.md"
        self.test_results: Dict[str, Dict[str, any]] = {}
        self.overall_start_time = time.time()
    
    def test_environment_setup(self) -> Tuple[bool, str, Dict[str, str]]:
        """測試環境設定"""
        start_time = time.time()
        details = {}
        
        try:
            # 檢查必要文件
            required_files = [
                "hrms.db",
                "db.py",
                "config.py",
                "requirements.txt"
            ]
            
            details["required_files"] = {}
            missing_files = []
            
            for file_path in required_files:
                full_path = self.project_root / file_path
                exists = full_path.exists()
                details["required_files"][file_path] = "存在" if exists else "缺失"
                if not exists:
                    missing_files.append(file_path)
            
            # 檢查資料庫大小
            db_path = self.project_root / "hrms.db"
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                details["database_size"] = f"{size_mb:.1f} MB"
            
            # 檢查 Python 環境
            details["python_version"] = sys.version
            details["platform"] = platform.platform()
            
            # 檢查環境變量
            details["env_vars"] = {
                "QT_QPA_PLATFORM": os.environ.get('QT_QPA_PLATFORM', '未設置'),
                "DB_URL": os.environ.get('DB_URL', '未設置'),
                "APP_NAME": os.environ.get('APP_NAME', '未設置')
            }
            
            duration = time.time() - start_time
            
            if missing_files:
                return False, f"缺少必要文件: {', '.join(missing_files)}", details
            
            return True, "環境設定正常", details
            
        except Exception as e:
            duration = time.time() - start_time
            return False, f"測試失敗: {str(e)}", {}
    
    def test_database_connection(self) -> Tuple[bool, str, Dict[str, any]]:
        """測試資料庫連接"""
        start_time = time.time()
        details = {}
        
        try:
            # 測試模組導入
            import db
            from config import settings
            from sqlalchemy import create_engine, inspect, text
            
            details["db_module"] = "導入成功"
            details["db_url"] = settings.db_url
            
            # 測試連接
            engine = create_engine(settings.db_url)
            details["engine_creation"] = "成功"
            
            # 測試基本查詢
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                query_result = result.scalar()
                
            if query_result == 1:
                details["connection_test"] = "成功"
            else:
                return False, "連接測試失敗", details
            
            # 檢查表格
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            details["total_tables"] = len(tables)
            details["table_list"] = tables
            
            # 取得主要表格的記錄數
            main_tables = ['basic', 'section', 'area', 'job', 'certification', 'vac_type']
            table_counts = {}
            
            with engine.connect() as conn:
                for table_name in main_tables:
                    if table_name in tables:
                        try:
                            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                            count = count_result.scalar()
                            table_counts[table_name] = count
                        except:
                            table_counts[table_name] = 0
            
            details["table_counts"] = table_counts
            
            duration = time.time() - start_time
            
            if len(tables) == 0:
                return False, "資料庫中沒有表格", details
            
            return True, f"連接正常，共 {len(tables)} 個表格", details
            
        except Exception as e:
            duration = time.time() - start_time
            return False, f"測試失敗: {str(e)}", {}
    
    def test_pyside6_environment(self) -> Tuple[bool, str, Dict[str, str]]:
        """測試 PySide6 環境"""
        start_time = time.time()
        details = {}
        
        try:
            from PySide6 import QtCore, QtWidgets, QtGui
            
            details["pyside6_import"] = "成功"
            details["qt_version"] = QtCore.qVersion()
            details["binding_version"] = QtCore.__version__
            
            # 創建應用程式實例
            app = QtWidgets.QApplication.instance()
            if app is None:
                app = QtWidgets.QApplication([])
            
            details["app_creation"] = "成功"
            
            # 測試主要元件
            widget = QtWidgets.QWidget()
            button = QtWidgets.QPushButton("Test")
            layout = QtWidgets.QVBoxLayout()
            
            details["widget_creation"] = "成功"
            details["qt_platform"] = QtCore.QCoreApplication.platformName()
            
            duration = time.time() - start_time
            return True, f"Qt {details['qt_version']} 正常", details
            
        except Exception as e:
            duration = time.time() - start_time
            return False, f"測試失敗: {str(e)}", {}
    
    def test_core_modules(self) -> Tuple[bool, str, Dict[str, any]]:
        """測試核心模組 (共 12 個)"""
        start_time = time.time()
        details = {"modules_tested": 0, "successful": 0, "failed": 0, "failures": []}
        
        # 12 個主要功能模組
        modules_to_test = [
            ("hrms.ui.qt.windows.start_page_new", "系統主頁面"),
            ("hrms.ui.qt.windows.basic_window_new", "員工基本資料管理"),
            ("hrms.ui.qt.windows.dept_window_new", "部門管理"),
            ("hrms.ui.qt.windows.area_window_new", "區域管理"),
            ("hrms.ui.qt.windows.job_window_new", "職務管理"),
            ("hrms.ui.qt.windows.shift_window_new", "班別管理"),
            ("hrms.ui.qt.windows.certify_items_window_new", "證照項目管理"),
            ("hrms.ui.qt.windows.certify_record_window_new", "證照記錄管理"),
            ("hrms.ui.qt.windows.training_record_window_new", "訓練記錄管理"),
            ("hrms.ui.qt.windows.vac_type_window_new", "假別管理"),
            ("hrms.ui.qt.windows.authority_window", "權限管理"),
            ("hrms.ui.qt.windows.shop_window", "店鋪管理"),
        ]
        
        try:
            for module_path, module_name in modules_to_test:
                try:
                    importlib.import_module(module_path)
                    details["successful"] += 1
                except Exception as e:
                    details["failed"] += 1
                    details["failures"].append(f"{module_name}: {str(e)}")
            
            details["modules_tested"] = len(modules_to_test)
            
            duration = time.time() - start_time
            
            if details["failed"] == 0:
                return True, f"所有 {details['successful']} 個模組導入成功", details
            else:
                return False, f"{details['successful']} 成功，{details['failed']} 失敗", details
                
        except Exception as e:
            duration = time.time() - start_time
            return False, f"測試失敗: {str(e)}", {}
    
    def test_repositories(self) -> Tuple[bool, str, Dict[str, any]]:
        """測試 Repository 層"""
        start_time = time.time()
        details = {"repositories_tested": 0, "successful": 0, "failed": 0, "failures": []}
        
        repositories_to_test = [
            ("repositories.base", "BaseRepository"),
            ("repositories.employee", "EmployeeRepository"),
            ("repositories.employee_repo", "EmployeeRepo"),
            ("repositories.authority", "AuthorityRepository"),
            ("repositories.certification", "CertificationRepository"),
            ("repositories.lookup", "LookupService"),
        ]
        
        try:
            # 測試 Unit of Work
            from hrms.core.db.unit_of_work_sqlite import UnitOfWork
            details["unit_of_work"] = "導入成功"
            
            # 測試各個 Repository
            for module_path, class_name in repositories_to_test:
                try:
                    module = importlib.import_module(module_path)
                    details["successful"] += 1
                except Exception as e:
                    details["failed"] += 1
                    details["failures"].append(f"{class_name}: {str(e)}")
            
            details["repositories_tested"] = len(repositories_to_test) + 1  # +1 for UnitOfWork
            
            duration = time.time() - start_time
            
            if details["failed"] == 0:
                return True, f"所有 Repository 模組正常", details
            else:
                return False, f"{details['successful']} 成功，{details['failed']} 失敗", details
                
        except Exception as e:
            duration = time.time() - start_time
            return False, f"測試失敗: {str(e)}", {}
    
    def test_domain_models(self) -> Tuple[bool, str, Dict[str, any]]:
        """測試 Domain Models"""
        start_time = time.time()
        details = {"models_tested": 0, "successful": 0, "failed": 0}
        
        try:
            # 測試主要的 domain models
            models_to_test = [
                ("domain.models", ["Basic", "Section", "Area", "Job", "Shift"]),
                ("hrms.persons.models", ["Person", "PersonInfo"]),
            ]
            
            for module_path, model_names in models_to_test:
                try:
                    module = importlib.import_module(module_path)
                    for model_name in model_names:
                        if hasattr(module, model_name):
                            details["successful"] += 1
                        else:
                            details["failed"] += 1
                except Exception as e:
                    details["failed"] += len(model_names)
            
            details["models_tested"] = sum(len(models) for _, models in models_to_test)
            
            duration = time.time() - start_time
            
            if details["failed"] == 0:
                return True, f"所有 {details['successful']} 個 Domain Models 正常", details
            else:
                return False, f"{details['successful']} 成功，{details['failed']} 失敗", details
                
        except Exception as e:
            duration = time.time() - start_time
            return False, f"測試失敗: {str(e)}", {}
    
    def test_application_startup(self) -> Tuple[bool, str, Dict[str, any]]:
        """測試應用程序啟動"""
        start_time = time.time()
        details = {}
        
        try:
            from PySide6.QtWidgets import QApplication
            from hrms.ui.qt.windows.start_page_new import StartPage
            
            # 創建應用程式
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            details["app_creation"] = "成功"
            
            # 嘗試創建主視窗
            window = StartPage()
            details["window_creation"] = "成功"
            details["window_title"] = window.windowTitle()
            details["window_size"] = f"{window.size().width()}x{window.size().height()}"
            
            duration = time.time() - start_time
            
            return True, "應用程序可正常啟動", details
            
        except Exception as e:
            duration = time.time() - start_time
            return False, f"測試失敗: {str(e)}", {}
    
    def run_all_tests(self) -> Dict[str, any]:
        """執行所有測試"""
        test_suite = [
            ("環境設定", self.test_environment_setup),
            ("資料庫連接", self.test_database_connection),
            ("PySide6 環境", self.test_pyside6_environment),
            ("核心功能模組 (12個)", self.test_core_modules),
            ("Repository 層", self.test_repositories),
            ("Domain Models", self.test_domain_models),
            ("應用程序啟動", self.test_application_startup),
        ]
        
        print("=" * 80)
        print("HRMS 最終完整測試")
        print("=" * 80)
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"專案路徑: {self.project_root}")
        print(f"Python: {sys.version}")
        print("=" * 80)
        print()
        
        for test_name, test_func in test_suite:
            print(f"【{test_name}】執行中...")
            success, message, details = test_func()
            
            self.test_results[test_name] = {
                "success": success,
                "message": message,
                "details": details,
            }
            
            status = "✅ 通過" if success else "❌ 失敗"
            print(f"  {status} - {message}")
            print()
        
        total_duration = time.time() - self.overall_start_time
        
        # 計算總結
        total_tests = len(test_suite)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_duration": total_duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "overall_status": "✅ 所有測試通過" if failed_tests == 0 else "❌ 部分測試失敗"
        }
        
        return summary
    
    def generate_markdown_report(self, summary: Dict[str, any]) -> str:
        """生成 Markdown 格式的報告"""
        lines = [
            "# HRMS 最終完整測試報告",
            "",
            f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**測試環境**: {platform.platform()}",
            f"**Python 版本**: {sys.version}",
            f"**專案路徑**: `{self.project_root}`",
            "",
            "## 測試總覽",
            "",
            f"- **總測試項目**: {summary['total_tests']}",
            f"- **通過**: {summary['passed_tests']} ✅",
            f"- **失敗**: {summary['failed_tests']} ❌",
            f"- **總耗時**: {summary['total_duration']:.2f} 秒",
            f"- **整體狀態**: {summary['overall_status']}",
            "",
            "---",
            "",
        ]
        
        # 詳細測試結果
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["success"] else "❌"
            lines.append(f"## {status_icon} {test_name}")
            lines.append("")
            lines.append(f"**結果**: {result['message']}")
            lines.append("")
            
            if result["details"]:
                lines.append("**詳細資訊**:")
                lines.append("```")
                for key, value in result["details"].items():
                    if isinstance(value, dict):
                        lines.append(f"{key}:")
                        for sub_key, sub_value in value.items():
                            lines.append(f"  {sub_key}: {sub_value}")
                    else:
                        lines.append(f"{key}: {value}")
                lines.append("```")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # 環境資訊
        lines.append("## 環境資訊")
        lines.append("")
        lines.append("```")
        lines.append(f"作業系統: {platform.system()} {platform.release()}")
        lines.append(f"Python: {sys.version}")
        lines.append(f"專案路徑: {self.project_root}")
        lines.append(f"資料庫: {self.project_root / 'hrms.db'}")
        lines.append("```")
        lines.append("")
        
        # 建議
        if summary["failed_tests"] > 0:
            lines.append("## 建議")
            lines.append("")
            lines.append("⚠️ 部分測試失敗，建議檢查以下事項:")
            lines.append("")
            
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    lines.append(f"- **{test_name}**: {result['message']}")
            
            lines.append("")
            lines.append("請修復問題後重新執行測試。")
        else:
            lines.append("## 結論")
            lines.append("")
            lines.append("✅ **恭喜！所有測試已通過。**")
            lines.append("")
            lines.append("HRMS 應用程序可以正常運行。")
            lines.append("")
            lines.append("要啟動應用程序，請執行:")
            lines.append("```bash")
            lines.append("python3 hrms/ui/qt/start_app.py")
            lines.append("```")
        
        return "\n".join(lines)
    
    def save_report(self, report_content: str):
        """保存報告到文件"""
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ 測試報告已保存至: {self.report_file}")
        except Exception as e:
            print(f"❌ 無法保存報告: {str(e)}")
    
    def cleanup(self):
        """清理資源"""
        try:
            # 清理 Qt 應用程式
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                app.quit()
        except:
            pass

def main():
    """主函數"""
    print("啟動 HRMS 最終完整測試...")
    print()
    
    tester = HRMSFinalTester()
    
    try:
        # 執行所有測試
        summary = tester.run_all_tests()
        
        # 生成報告
        print("生成測試報告...")
        report_content = tester.generate_markdown_report(summary)
        
        # 保存報告
        tester.save_report(report_content)
        
        # 顯示報告摘要
        print()
        print("=" * 80)
        print("測試完成！")
        print("=" * 80)
        print(f"整體狀態: {summary['overall_status']}")
        print(f"總耗時: {summary['total_duration']:.2f} 秒")
        print(f"通過: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"失敗: {summary['failed_tests']}/{summary['total_tests']}")
        print("=" * 80)
        
        # 清理
        tester.cleanup()
        
        # 返回適當的退出碼
        sys.exit(0 if summary["failed_tests"] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 測試被使用者中斷")
        tester.cleanup()
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 測試執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        tester.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
