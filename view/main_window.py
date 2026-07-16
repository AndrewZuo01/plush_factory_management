# view/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
)
from config import MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT, MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT
from view import QuotePricePage, ScheduleDashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("毛绒玩具报价与工期排期管理系统")
        self.resize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setMinimumSize(MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # 左侧导航栏
        nav_layout = QVBoxLayout()
        btn_quote = QPushButton("报价计算")
        btn_dashboard = QPushButton("排期Dashboard")
        nav_layout.addWidget(btn_quote)
        nav_layout.addWidget(btn_dashboard)
        nav_layout.addStretch()

        # 页面堆栈
        self.stack = QStackedWidget()
        self.page_quote = QuotePricePage()
        self.page_dash = ScheduleDashboardPage()
        self.stack.addWidget(self.page_quote)
        self.stack.addWidget(self.page_dash)

        # 绑定切换
        btn_quote.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        main_layout.addLayout(nav_layout, stretch=1)
        main_layout.addWidget(self.stack, stretch=9)
