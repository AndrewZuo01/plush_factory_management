# view/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout
)
from config import MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT, MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT
from view import QuotePricePage, ScheduleDashboardPage, ProcessStatPage


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

        # 左侧导航栏【新增工序统计按钮】
        nav_layout = QVBoxLayout()
        btn_quote = QPushButton("报价计算")
        btn_dashboard = QPushButton("排期Dashboard")
        btn_stat = QPushButton("工序工期统计报表")
        nav_layout.addWidget(btn_quote)
        nav_layout.addWidget(btn_dashboard)
        nav_layout.addWidget(btn_stat)
        nav_layout.addStretch()

        # 页面堆栈【新增统计页面】
        self.stack = QStackedWidget()
        self.page_quote = QuotePricePage()
        self.page_dash = ScheduleDashboardPage()
        self.page_stat = ProcessStatPage()
        self.stack.addWidget(self.page_quote)    # index 0
        self.stack.addWidget(self.page_dash)     # index 1
        self.stack.addWidget(self.page_stat)     # index 2

        # 绑定切换事件
        btn_quote.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_stat.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        main_layout.addLayout(nav_layout, stretch=1)
        main_layout.addWidget(self.stack, stretch=9)
