# view/pages/schedule_dashboard.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QMessageBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt

from view.widgets import PriceSpinBox, DateTimeEdit
from service.schedule_track_service import (
    init_empty_schedule,
    get_schedule_dashboard_data,
    save_schedule_field,
    check_time_valid
)
from database.models.quote_model import get_all_quote_list
from utils import app_log


class ScheduleDashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.quote_id = None
        self.schedule_widget_map = {}
        self.init_ui()
        self.load_quote_selector()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12,12,12,12)
        main_layout.setSpacing(10)

        # 顶部操作栏
        top_bar = QHBoxLayout()
        self.label_quote_tip = QLabel("请先选择上方报价单")
        self.btn_load_quote = QPushButton("刷新报价列表")
        self.btn_init_schedule = QPushButton("初始化该报价排期")
        self.btn_refresh = QPushButton("刷新看板数据")

        self.btn_load_quote.clicked.connect(self.load_quote_selector)
        self.btn_init_schedule.clicked.connect(self.do_init_schedule)
        self.btn_refresh.clicked.connect(self.refresh_dashboard)

        top_bar.addWidget(self.label_quote_tip)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_load_quote)
        top_bar.addWidget(self.btn_init_schedule)
        top_bar.addWidget(self.btn_refresh)
        main_layout.addLayout(top_bar)

        # 滚动区域承载所有工序卡片
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # 底部汇总信息
        bottom_group = QGroupBox("整体项目汇总")
        bottom_layout = QHBoxLayout(bottom_group)
        self.lbl_plan_total = QLabel("计划总工期：0 天")
        self.lbl_actual_total = QLabel("实际总工期：0 天")
        self.lbl_cost_total = QLabel("实际总成本：0.00 元")
        self.lbl_delay_flag = QLabel("整体状态：正常")
        bottom_layout.addWidget(self.lbl_plan_total)
        bottom_layout.addWidget(self.lbl_actual_total)
        bottom_layout.addWidget(self.lbl_cost_total)
        bottom_layout.addWidget(self.lbl_delay_flag)
        main_layout.addWidget(bottom_group)

    def load_quote_selector(self):
        """加载所有报价单，供选择绑定排期"""
        quote_list = get_all_quote_list()
        if not quote_list:
            self.label_quote_tip.setText("暂无报价单，请先去报价页面新建报价")
            self.quote_id = None
            return

        tip_text = "可选择报价："
        for q in quote_list[:5]:
            tip_text += f"【{q['id']}:{q['toy_name']}】"
        self.label_quote_tip.setText(tip_text)
        # 默认选中最新一条
        self.quote_id = quote_list[0]["id"]
        app_log.info(f"默认加载报价单ID:{self.quote_id}")
        self.refresh_dashboard()

    def do_init_schedule(self):
        if not self.quote_id:
            QMessageBox.warning(self, "提示", "未选中任何报价单")
            return
        try:
            init_empty_schedule(self.quote_id)
            QMessageBox.information(self, "成功", "排期工序初始化完成")
            self.refresh_dashboard()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            app_log.error("初始化排期失败", exc_info=True)

    def refresh_dashboard(self):
        if not self.quote_id:
            return
        try:
            dash_data = get_schedule_dashboard_data(self.quote_id)
            # 清空原有卡片
            for i in reversed(range(self.scroll_layout.count())):
                item = self.scroll_layout.itemAt(i)
                if item.widget():
                    item.widget().deleteLater()
            self.schedule_widget_map.clear()

            # 逐个生成工序卡片
            for item in dash_data["process_list"]:
                card = self.create_process_card(item)
                self.scroll_layout.addWidget(card)

            # 刷新底部汇总
            self.lbl_plan_total.setText(f"计划总工期：{dash_data['total_plan_days']} 天")
            self.lbl_actual_total.setText(f"实际总工期：{dash_data['total_actual_days']} 天")
            self.lbl_cost_total.setText(f"实际总成本：{dash_data['total_actual_cost']} 元")
            if dash_data["is_all_delay"]:
                self.lbl_delay_flag.setText("整体状态：存在延期")
                self.lbl_delay_flag.setStyleSheet("color:red;font-weight:bold;")
            else:
                self.lbl_delay_flag.setText("整体状态：正常")
                self.lbl_delay_flag.setStyleSheet("color:green;font-weight:bold;")
        except Exception as e:
            QMessageBox.critical(self, "读取排期失败", str(e))
            app_log.error("刷新看板异常", exc_info=True)

    def create_process_card(self, data: dict):
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        layout = QGridLayout(frame)
        sid = data["id"]

        # 工序名称+状态
        layout.addWidget(QLabel(f"【{data['process_name']}】状态：{data['status']}"), 0, 0, 1, 4)

        # 计划时间
        layout.addWidget(QLabel("计划开始"), 1, 0)
        plan_start = DateTimeEdit()
        plan_start.set_datetime_text(data["plan_start"])
        layout.addWidget(plan_start, 1, 1)

        layout.addWidget(QLabel("计划结束"), 1, 2)
        plan_end = DateTimeEdit()
        plan_end.set_datetime_text(data["plan_end"])
        layout.addWidget(plan_end, 1, 3)

        # 实际时间
        layout.addWidget(QLabel("实际开始"), 2, 0)
        actual_start = DateTimeEdit()
        actual_start.set_datetime_text(data["actual_start"])
        layout.addWidget(actual_start, 2, 1)

        layout.addWidget(QLabel("实际结束"), 2, 2)
        actual_end = DateTimeEdit()
        actual_end.set_datetime_text(data["actual_end"])
        layout.addWidget(actual_end, 2, 3)

        # 实际成本
        layout.addWidget(QLabel("本工序实际成本"), 3, 0)
        cost_spin = PriceSpinBox()
        cost_spin.setValue(data["actual_cost"])
        layout.addWidget(cost_spin, 3, 1)

        # 保存按钮
        btn_save = QPushButton("保存本条")
        layout.addWidget(btn_save, 3, 3)

        # 存入映射
        self.schedule_widget_map[sid] = {
            "plan_start": plan_start,
            "plan_end": plan_end,
            "actual_start": actual_start,
            "actual_end": actual_end,
            "cost": cost_spin
        }

        def save_single():
            widgets = self.schedule_widget_map[sid]
            ps = widgets["plan_start"].get_datetime_str()
            pe = widgets["plan_end"].get_datetime_str()
            as_ = widgets["actual_start"].get_datetime_str()
            ae = widgets["actual_end"].get_datetime_str()
            cost = widgets["cost"].get_value()

            # 校验计划时间
            ok, msg = check_time_valid(ps, pe)
            if ps and pe and not ok:
                QMessageBox.warning(self, "时间错误", msg)
                return

            update_dict = {
                "plan_start": ps,
                "plan_end": pe,
                "actual_start": as_,
                "actual_end": ae,
                "actual_cost": cost
            }
            save_schedule_field(sid, update_dict)
            QMessageBox.information(self, "提示", "已保存")
            self.refresh_dashboard()

        btn_save.clicked.connect(save_single)
        return frame
