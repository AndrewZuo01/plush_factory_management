# view/widgets/date_time_edit.py
from PySide6.QtWidgets import QDateTimeEdit
from PySide6.QtCore import QDateTime
from config import DATETIME_FORMAT


class DateTimeEdit(QDateTimeEdit):
    """
    全局统一格式的日期时间选择框
    绑定项目规定时间格式化字符串，读写格式完全统一
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置显示与解析格式
        self.setDisplayFormat(DATETIME_FORMAT)
        # 弹出日历选择面板
        self.setCalendarPopup(True)
        # 初始置空
        self.clear()

    def set_datetime_text(self, time_str: str):
        """
        传入字符串时间赋值，空字符串则清空
        """
        if not time_str.strip():
            self.clear()
            return
        dt = QDateTime.fromString(time_str, DATETIME_FORMAT)
        if dt.isValid():
            self.setDateTime(dt)

    def get_datetime_str(self) -> str:
        """
        获取格式化后的时间字符串，未填写返回空串
        """
        if not self.hasFocus() and self.lineEdit().text().strip() == "":
            return ""
        current_dt = self.dateTime()
        return current_dt.toString(DATETIME_FORMAT)

    def clear(self):
        """清空输入框内容"""
        self.lineEdit().clear()
