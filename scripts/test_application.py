#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRMS 應用程序啟動測試腳本
測試應用程序是否能夠正常啟動和運行
"""

import os
import sys
import time
import traceback
import logging
from datetime import datetime
from pathlib import Path

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApplicationTester:
    """應用程序測試器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = Path(__file__).parent
        self.report_file = self.scripts_dir / "application_test_report.txt"
        self.test_results = {
            "environment_setup": {"status": "未開始", "message": ""},
            "module_imports": {"status": "未開始", "message": ""},
            "app_initialization": {"status": "未開始", "message": ""},
            "main_window_load": {"status": "未開始", "message": ""},
            "overall_result": {"status": "未開始", "message": ""}
        }
        
    def setup_environment(self):
        """設定測試環境"""
        logger.info("設定測試環境...")
        
        # 設定顯示環境變數（使用離線渲染，不需要顯示服務器）
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/usr/lib/x86_64-linux-gnu/qt6/plugins/platforms'
        
        # 設定項目路徑
        sys.path.insert(0, str(self.project_root))
        
        # 設定資料庫
        os.environ.setdefault('DB_URL', 'sqlite:///./hrms.db')
        os.environ.setdefault('APP_NAME', 'HRMS SQLite')
        
        # 檢查必要的資料庫檔案
        db_file = self.project_root / "hrms.db"
        if db_file.exists():
            logger.info(f"資料庫檔案已存在: {db_file}")
            self.test_results["environment_setup"] = {
                "status": "成功",
                "message": f"資料庫檔案存在 ({db_file.stat().st_size} bytes)"
            }
        else:
            logger.warning(f"資料庫檔案不存在: {db_file}")
            self.test_results["environment_setup"] = {
                "status": "警告",
                "message": f"資料庫檔案不存在，將會自動創建"
            }
        
        return True
        
    def test_module_imports(self):
        """測試模組導入"""
        logger.info("測試模組導入...")
        
        import_errors = []
        
        # 測試核心模組
        modules_to_test = [
            ("PySide6.QtWidgets", "Qt Widgets"),
            ("PySide6.QtCore", "Qt Core"),
            ("hrms.ui.qt.windows.start_page_new", "Start Page"),
            ("db", "Database Module"),
            ("config", "Config Module"),
        ]
        
        for module_name, display_name in modules_to_test:
            try:
                __import__(module_name)
                logger.info(f"✓ {display_name} 模組導入成功")
            except ImportError as e:
                error_msg = f"✗ {display_name} 模組導入失敗: {str(e)}"
                logger.error(error_msg)
                import_errors.append(error_msg)
            except Exception as e:
                error_msg = f"✗ {display_name} 模組載入錯誤: {str(e)}"
                logger.error(error_msg)
                import_errors.append(error_msg)
        
        # 附加測試其他 UI 視窗
        ui_modules = [
            "hrms.ui.qt.windows.basic_window_new",
            "hrms.ui.qt.windows.dept_window_new", 
            "hrms.ui.qt.windows.area_window_new",
            "hrms.ui.qt.windows.job_window_new",
        ]
        
        for module_name in ui_modules:
            try:
                __import__(module_name)
                logger.info(f"✓ UI 模組 {module_name} 導入成功")
            except ImportError as e:
                logger.warning(f"⚠ UI 模組 {module_name} 導入失敗: {str(e)}")
        
        if import_errors:
            self.test_results["module_imports"] = {
                "status": "失敗",
                "message": "\n".join(import_errors)
            }
            return False
        else:
            self.test_results["module_imports"] = {
                "status": "成功",
                "message": "所有核心模組導入成功"
            }
            return True
    
    def test_app_initialization(self):
        """測試應用程序初始化"""
        logger.info("測試應用程序初始化...")
        
        try:
            # 導入必要的模組
            from PySide6.QtWidgets import QApplication
            import sys
            
            # 創建應用程序實例
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)
            
            logger.info("✓ QApplication 實例創建成功")
            
            # 設定應用程式樣式
            self.app.setStyle("Fusion")
            logger.info("✓ 應用程式樣式設置成功")
            
            self.test_results["app_initialization"] = {
                "status": "成功",
                "message": "應用程序初始化成功"
            }
            return True
            
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"應用程序初始化失敗: {str(e)}")
            logger.error(f"詳細錯誤:\n{error_traceback}")
            
            self.test_results["app_initialization"] = {
                "status": "失敗",
                "message": f"{str(e)}\n{error_traceback}"
            }
            return False
    
    def test_main_window_load(self):
        """測試主視窗載入"""
        logger.info("測試主視窗載入...")
        
        try:
            from hrms.ui.qt.windows.start_page_new import StartPage
            
            # 創建主視窗
            start_time = time.time()
            self.main_window = StartPage()
            load_time = time.time() - start_time
            
            logger.info(f"✓ 主視窗載入成功 (耗時: {load_time:.2f}秒)")
            logger.info(f"✓ 主視窗標題: {self.main_window.windowTitle()}")
            logger.info(f"✓ 主視窗大小: {self.main_window.size().width()}x{self.main_window.size().height()}")
            
            self.test_results["main_window_load"] = {
                "status": "成功",
                "message": f"主視窗載入成功 (耗時: {load_time:.2f}秒)"
            }
            return True
            
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"主視窗載入失敗: {str(e)}")
            logger.error(f"詳細錯誤:\n{error_traceback}")
            
            self.test_results["main_window_load"] = {
                "status": "失敗",
                "message": f"{str(e)}\n{error_traceback}"
            }
            return False
    
    def generate_report(self):
        """生成測試報告"""
        logger.info("生成測試報告...")
        
        report_lines = [
            "=" * 80,
            "HRMS 應用程序啟動測試報告",
            "=" * 80,
            f"測試日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Python版本: {sys.version}",
            f"系統: {sys.platform}",
            "=" * 80,
            "",
        ]
        
        # 測試項目結果
        test_items = [
            ("環境設定", "environment_setup"),
            ("模組導入", "module_imports"),
            ("應用程序初始化", "app_initialization"),
            ("主視窗載入", "main_window_load"),
        ]
        
        for display_name, test_key in test_items:
            result = self.test_results[test_key]
            status = result["status"]
            message = result["message"]
            
            report_lines.append(f"【{display_name}】")
            report_lines.append(f"  狀態: {status}")
            if message:
                report_lines.append(f"  說明: {message}")
            report_lines.append("")
        
        # 整體結果
        failed_tests = [
            key for key, result in self.test_results.items() 
            if result["status"] == "失敗" and key != "overall_result"
        ]
        
        if failed_tests:
            overall_status = "失敗"
            overall_message = f"以下測試項目失敗: {', '.join(failed_tests)}"
        else:
            overall_status = "成功"
            overall_message = "所有測試項目均成功"
        
        self.test_results["overall_result"] = {
            "status": overall_status,
            "message": overall_message
        }
        
        report_lines.append("" * 80)
        report_lines.append(f"【整體結果】")
        report_lines.append(f"  狀態: {overall_status}")
        report_lines.append(f"  說明: {overall_message}")
        report_lines.append("" * 80)
        
        # 環境資訊
        report_lines.append("【環境資訊】")
        report_lines.append(f"  工作目錄: {os.getcwd()}")
        report_lines.append(f"  PYTHONPATH: {sys.path}")
        report_lines.append(f"  QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM', '未設定')}")
        
        # 嘗試獲取 Qt 版本
        try:
            from PySide6 import QtCore
            qt_version = QtCore.qVersion()
            report_lines.append(f"  Qt版本: {qt_version}")
        except:
            report_lines.append("  Qt版本: 無法檢測")
        
        report_lines.append("=" * 80)
        
        # 寫入報告檔案
        report_content = "\n".join(report_lines)
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"測試報告已生成: {self.report_file}")
        return report_content
    
    def run_all_tests(self):
        """執行所有測試"""
        logger.info("開始執行 HRMS 應用程序測試...")
        
        # 測試步驟
        test_steps = [
            ("環境設定", self.setup_environment),
            ("模組導入", self.test_module_imports),
            ("應用程序初始化", self.test_app_initialization),
            ("主視窗載入", self.test_main_window_load),
        ]
        
        all_passed = True
        for step_name, test_func in test_steps:
            logger.info(f"\n{'='*60}")
            logger.info(f"執行: {step_name}")
            logger.info(f"{'='*60}")
            
            try:
                success = test_func()
                if not success:
                    logger.warning(f"⚠ {step_name} 測試未通過")
                    all_passed = False
            except Exception as e:
                logger.error(f"✗ {step_name} 測試執行失敗: {str(e)}")
                logger.error(traceback.format_exc())
                all_passed = False
        
        # 生成報告
        self.generate_report()
        
        logger.info(f"\n{'='*60}")
        logger.info("測試完成！")
        logger.info(f"{'='*60}")
        
        # 清理
        try:
            if hasattr(self, 'app'):
                self.app.quit()
        except:
            pass
        
        return all_passed

def main():
    """主函數"""
    tester = ApplicationTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("✓ 所有測試通過")
        sys.exit(0)
    else:
        logger.error("✗ 部分測試失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()