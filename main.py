# main.py
import sys
from PySide6.QtWidgets import QApplication
from database import init_database
from view import MainWindow

if __name__ == "__main__":
    # 初始化数据库，不存在则建表
    init_database()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
