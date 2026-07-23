# view/pages/process_stat_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QGroupBox, QLabel, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from service.process_stat_service import calc_process_stat_data
from utils import app_log


class ProcessStatPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_stat_table()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 顶部操作栏
        top_bar = QHBoxLayout()
        self.label_tip = QLabel("说明：统计时自动剔除每道工序实际工期的最大、最小值各一条")
        self.btn_refresh = QPushButton("重新计算统计数据")
        self.btn_refresh.clicked.connect(self.refresh_stat_table)
        top_bar.addWidget(self.label_tip)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_refresh)
        main_layout.addLayout(top_bar)

        # 统计表格
        table_group = QGroupBox("各工序工期统计报表")
        table_layout = QVBoxLayout(table_group)
        self.stat_table = QTableWidget()
        # 表头
        headers = ["工序名称", "平均计划工期(天)", "原始数据条数", "剔除极值后条数", "平均实际工期(天)", "平均差值(实际-计划)"]
        self.stat_table.setColumnCount(len(headers))
        self.stat_table.setHorizontalHeaderLabels(headers)
        # 自适应列宽
        self.stat_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.stat_table)
        main_layout.addWidget(table_group)

    def refresh_stat_table(self):
        """刷新统计表格数据"""
        try:
            stat_list = calc_process_stat_data()
            self.stat_table.setRowCount(len(stat_list))
            for row, item in enumerate(stat_list):
                data = [
                    item["process_name"],
                    str(item["std_plan_days"]),
                    str(item["origin_data_count"]),
                    str(item["filter_data_count"]),
                    str(item["avg_actual_days"]),
                    str(item["avg_diff_days"])
                ]
                for col, text in enumerate(data):
                    cell = QTableWidgetItem(text)
                    cell.setTextAlignment(Qt.AlignCenter)
                    # 差值正数标红、负数标绿
                    if col == 5:
                        val = float(text)
                        if val > 0:
                            cell.setForeground(Qt.red)
                        elif val < 0:
                            cell.setForeground(Qt.green)
                    self.stat_table.setItem(row, col, cell)
        except Exception as e:
            QMessageBox.critical(self, "统计失败", f"计算报表出错：{str(e)}")
            app_log.error("工序统计报表加载失败", exc_info=True)
