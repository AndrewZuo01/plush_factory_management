# view/widgets/number_spin.py
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtCore import Qt
from config import PRICE_DECIMAL_PLACES, MIN_PRICE_VALUE


class PriceSpinBox(QDoubleSpinBox):
    """
    专用金额输入框
    限定最小0，固定小数位数，禁止负数，对齐右对齐
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 小数位数
        self.setDecimals(PRICE_DECIMAL_PLACES)
        # 最小值
        self.setMinimum(MIN_PRICE_VALUE)
        # 最大值给一个很大的上限防止超限
        self.setMaximum(999999.99)
        # 步长0.01
        self.setSingleStep(0.01)
        # 右对齐
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def keyPressEvent(self, event):
        """拦截非法输入，只允许数字、小数点、退格、删除"""
        allowed_keys = {
            Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4,
            Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9,
            Qt.Key_Period, Qt.Key_Backspace, Qt.Key_Delete,
            Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End
        }
        if event.key() not in allowed_keys:
            event.ignore()
        else:
            super().keyPressEvent(event)

    def get_value(self):
        """直接获取格式化后数值"""
        return round(self.value(), PRICE_DECIMAL_PLACES)
