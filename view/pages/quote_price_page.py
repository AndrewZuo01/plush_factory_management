# view/pages/quote_price_page.py
import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QGroupBox, QFrame, QSpacerItem, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from config import TOY_IMG_DIR, ADJUST_RATIO_OPTIONS
from view.widgets import PriceSpinBox
from service.quote_calc_service import (
    get_default_process_price_list,
    batch_adjust_price,
    calc_total_price,
    save_new_quote
)
from utils import not_empty, app_log


class QuotePricePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process_spin_map = {}  # 保存 {process_id: spin_box}
        self.init_ui()
        self.load_default_process()

    def init_ui(self):
        # 整体左右布局
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ========== 左侧：玩具预览 + 基础信息 ==========
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 基础信息组
        info_group = QGroupBox("报价基础信息")
        info_layout = QGridLayout(info_group)
        self.edit_toy_name = QLineEdit()
        self.edit_toy_name.setPlaceholderText("请输入毛绒玩具名称")
        self.edit_remark = QTextEdit()
        self.edit_remark.setPlaceholderText("备注信息（可选）")
        self.edit_remark.setMaximumHeight(80)

        info_layout.addWidget(QLabel("玩具名称："), 0, 0)
        info_layout.addWidget(self.edit_toy_name, 0, 1)
        info_layout.addWidget(QLabel("备注："), 1, 0)
        info_layout.addWidget(self.edit_remark, 1, 1)

        # 玩具图片预览
        img_group = QGroupBox("玩具预览图")
        img_layout = QVBoxLayout(img_group)
        self.label_toy_img = QLabel("暂无图片")
        self.label_toy_img.setMinimumSize(400, 350)
        self.label_toy_img.setStyleSheet("background-color:#f6f6f6;")
        self.label_toy_img.setAlignment(Qt.AlignCenter)

        # 默认加载占位图
        default_img_path = os.path.join(TOY_IMG_DIR, "default.png")
        if os.path.exists(default_img_path):
            pix = QPixmap(default_img_path)
            self.label_toy_img.setPixmap(pix.scaled(
                self.label_toy_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

        img_layout.addWidget(self.label_toy_img)

        left_layout.addWidget(info_group)
        left_layout.addWidget(img_group)
        main_layout.addWidget(left_widget, stretch=6)

        # ========== 右侧：工序价格列表 + 批量调价 + 总价 + 保存 ==========
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 工序列表区域
        process_group = QGroupBox("工序单价调整")
        self.process_layout = QGridLayout(process_group)

        # 批量调价按钮组
        adjust_group = QGroupBox("整体批量调价")
        adjust_layout = QHBoxLayout(adjust_group)
        self.adjust_btns = {}
        for name, ratio in ADJUST_RATIO_OPTIONS.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, r=ratio: self.do_batch_adjust(r))
            adjust_layout.addWidget(btn)
            self.adjust_btns[name] = btn

        # 总价展示
        total_group = QGroupBox("报价总价")
        total_layout = QHBoxLayout(total_group)
        self.label_total_price = QLabel("0.00 元")
        self.label_total_price.setStyleSheet("font-size:18px;color:#e74c3c;font-weight:bold;")
        self.label_total_price.setAlignment(Qt.AlignCenter)
        total_layout.addWidget(self.label_total_price)

        # 功能按钮
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("新建报价")
        self.btn_save = QPushButton("保存报价单")
        self.btn_new.clicked.connect(self.clear_page)
        self.btn_save.clicked.connect(self.save_quote)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_save)

        right_layout.addWidget(process_group)
        right_layout.addWidget(adjust_group)
        right_layout.addWidget(total_group)
        right_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(right_widget, stretch=4)

    def load_default_process(self):
        """加载默认工序和默认单价"""
        self.process_spin_map.clear()
        process_list = get_default_process_price_list()

        # 清空布局
        for i in reversed(range(self.process_layout.count())):
            self.process_layout.itemAt(i).widget().deleteLater()

        # 动态生成每一行工序
        for row, (pid, price) in enumerate(process_list):
            name_label = QLabel("")
            spin = PriceSpinBox()
            spin.setValue(price)
            spin.valueChanged.connect(self.refresh_total_price)

            self.process_layout.addWidget(name_label, row, 0)
            self.process_layout.addWidget(spin, row, 1)

            self.process_spin_map[pid] = (name_label, spin)

        # 回填工序名称
        from database.models.quote_model import get_all_process
        full_process = get_all_process()
        for p in full_process:
            if p["id"] in self.process_spin_map:
                lab, _ = self.process_spin_map[p["id"]]
                lab.setText(p["process_name"])

        self.refresh_total_price()

    def get_current_process_price_list(self):
        """获取当前界面所有工序价格"""
        res = []
        for pid, (_, spin) in self.process_spin_map.items():
            res.append((pid, spin.get_value()))
        return res

    def refresh_total_price(self):
        """实时刷新总价"""
        price_list = self.get_current_process_price_list()
        total = calc_total_price(price_list)
        self.label_total_price.setText(f"{total} 元")

    def do_batch_adjust(self, ratio: float):
        """批量整体调价"""
        origin_list = self.get_current_process_price_list()
        new_list = batch_adjust_price(origin_list, ratio)

        # 回填UI
        for pid, new_price in new_list:
            if pid in self.process_spin_map:
                _, spin = self.process_spin_map[pid]
                spin.setValue(new_price)

        self.refresh_total_price()

    def save_quote(self):
        """保存报价单"""
        toy_name = self.edit_toy_name.text().strip()
        remark = self.edit_remark.toPlainText().strip()

        # 校验
        ok, tip = not_empty(toy_name, "玩具名称")
        if not ok:
            QMessageBox.warning(self, "提示", tip)
            return

        price_list = self.get_current_process_price_list()
        try:
            quote_id = save_new_quote(toy_name, remark, price_list)
            QMessageBox.information(self, "成功", f"报价单保存成功！ID:{quote_id}")
            app_log.info(f"用户保存报价单成功 ID={quote_id}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")
            app_log.error("保存报价单失败", exc_info=True)

    def clear_page(self):
        """新建报价，清空页面恢复默认价格"""
        self.edit_toy_name.clear()
        self.edit_remark.clear()
        self.load_default_process()
        self.refresh_total_price()
