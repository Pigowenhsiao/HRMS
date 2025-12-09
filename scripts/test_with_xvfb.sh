#!/bin/bash
# HRMS 應用程序測試腳本（使用 xvfb）

set -e

echo "=================================="
echo "HRMS 應用程序啟動測試"
echo "=================================="
echo "測試日期: $(date)"
echo "Python版本: $(python3 --version)"
echo ""

# 檢查 xvfb-run 是否可用
if ! command -v xvfb-run &> /dev/null; then
    echo "⚠  xvfb-run 未安裝，將嘗試離線渲染模式..."
    
    # 離線渲染模式
    export QT_QPA_PLATFORM=offscreen
    echo "使用 Qt 離線渲染平台: $QT_QPA_PLATFORM"
    echo ""
    
    # 執行測試
    echo "執行 Python 測試腳本..."
    cd "$(dirname "$0")/.."
    python3 scripts/test_application.py
    
else
    echo "✓ xvfb-run 已安裝，使用虛擬顯示測試..."
    
    # 使用 xvfb-run 執行測試
    echo "使用 xvfb-run 啟動虛擬顯示..."
    cd "$(dirname "$0")/.."
    
    xvfb-run -a -s "-screen 0 1024x768x24" \
        python3 scripts/test_application.py 2>&1 | tee /tmp/xvfb_test.log
    
    echo ""
    echo "xvfb 測試日誌已保存到: /tmp/xvfb_test.log"
fi

echo ""
echo "=================================="
echo "測試完成！"
echo "=================================="