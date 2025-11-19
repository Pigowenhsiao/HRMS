from PySide6.QtWidgets import QApplication
import sys
from .windows.start_page import StartPage

def main():
    app = QApplication(sys.argv)
    w = StartPage()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
