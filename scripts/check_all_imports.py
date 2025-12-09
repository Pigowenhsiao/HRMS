#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 模組導入測試腳本
測試所有 UI 模組是否可以正確導入
"""

import sys
import os
import importlib
import traceback
from typing import Dict, List, Tuple

# 將專案根目錄添加到 Python 路徑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_module_import(module_name: str) -> Tuple[bool, str]:
    """
    測試單個模組的導入
    
    Args:
        module_name: 模組名稱
        
    Returns:
        Tuple[是否成功, 訊息]
    """
    try:
        importlib.import_module(module_name)
        return True, "導入成功"
    except Exception as e:
        error_msg = f"導入失敗: {str(e)}"
        error_msg += f"\n錯誤類型: {type(e).__name__}"
        error_msg += f"\n詳細追蹤:\n{traceback.format_exc()}"
        return False, error_msg


def main():
    """主函數"""
    print("=" * 80)
    print("UI 模組導入測試報告")
    print("=" * 80)
    print(f"測試時間: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 需要測試的模組列表
    modules_to_test = [
        "hrms.ui.qt.windows.basic_window_new",
        "hrms.ui.qt.windows.dept_window_new",
        "hrms.ui.qt.windows.area_window_new",
        "hrms.ui.qt.windows.job_window_new",
        "hrms.ui.qt.windows.certify_items_window",
        "hrms.ui.qt.windows.certify_record_window",
        "hrms.ui.qt.windows.training_record_window",
        "hrms.ui.qt.windows.shop_window",
        "hrms.ui.qt.windows.certify_type_window",
        "hrms.ui.qt.windows.authority_window",
        "hrms.ui.qt.windows.vac_type_window",
        "hrms.ui.qt.windows.shift_window_new",
    ]
    
    results: Dict[str, Tuple[bool, str]] = {}
    
    # 測試每個模組
    for idx, module_name in enumerate(modules_to_test, 1):
        print(f"[{idx}/{len(modules_to_test)}] 測試模組: {module_name}")
        success, message = test_module_import(module_name)
        results[module_name] = (success, message)
        
        if success:
            print(f"    ✓ {message}")
        else:
            print(f"    ✗ {message.split(chr(10))[0]}")
        print()
    
    # 生成總結報告
    print("=" * 80)
    print("測試總結")
    print("=" * 80)
    
    successful = [name for name, (success, _) in results.items() if success]
    failed = [name for name, (success, _) in results.items() if not success]
    
    print(f"總計測試模組數: {len(modules_to_test)}")
    print(f"成功: {len(successful)} 個")
    print(f"失敗: {len(failed)} 個")
    print()
    
    if successful:
        print("成功的模組:")
        for name in successful:
            print(f"  ✓ {name}")
        print()
    
    if failed:
        print("失敗的模組:")
        for name in failed:
            print(f"  ✗ {name}")
        print()
        
        # 顯示詳細錯誤訊息
        print("詳細錯誤訊息:")
        print("-" * 80)
        for name in failed:
            _, error_msg = results[name]
            print(f"\n{name}:")
            print(error_msg)
            print("-" * 80)
    
    print()
    if failed:
        print("測試結果: 部分模組導入失敗 ❌")
        sys.exit(1)
    else:
        print("測試結果: 所有模組導入成功 ✅")
        sys.exit(0)


if __name__ == "__main__":
    main()
