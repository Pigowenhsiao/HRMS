from PySide6.QtWidgets import QApplication
import sys
from hrms.ui.qt.windows.start_page_new import StartPage

def main():
    """應用程式進入點"""
    app = QApplication(sys.argv)
    
    # 設定應用程式樣式
    app.setStyle("Fusion")
    
    # 建立並顯示主視窗
    window = StartPage()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
