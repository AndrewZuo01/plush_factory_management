# view/widgets/date_time_edit.py
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from datetime import datetime
from config import DATETIME_FORMAT


class DateTimeEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 提示文字，告诉用户填写格式
        self.setPlaceholderText("格式：2026-07-16 14:30")
        # 初始化清空
        self.clear()

    def clear(self):
        super().clear()

    def set_datetime_text(self, time_str: str):
        """外部赋值，自动标准化格式"""
        if not time_str or not time_str.strip():
            self.clear()
            return
        std_text = self._parse_any_input(time_str)
        if std_text:
            self.setText(std_text)
        else:
            self.clear()

    def get_datetime_str(self) -> str:
        """取值返回标准格式字符串，空则返回空串"""
        raw = self.text().strip()
        if not raw:
            return ""
        return self._parse_any_input(raw)

    def _parse_any_input(self, text: str) -> str:
        """
        兼容多种简写输入，统一转为 %Y-%m-%d %H:%M
        支持：
        2026-5-6
        2026-5-6 8:9
        2026-05-06 08:09
        无法解析返回空
        """
        text = text.strip()
        # 标准格式直接返回
        try:
            dt = datetime.strptime(text, DATETIME_FORMAT)
            return dt.strftime(DATETIME_FORMAT)
        except ValueError:
            pass

        # 只有日期，不带时分，默认 00:00
        try:
            dt = datetime.strptime(text, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d 00:00")
        except ValueError:
            pass

        # 简写日期+简写时分
        try:
            dt = datetime.strptime(text, "%Y-%m-%d %H:%M")
            return dt.strftime(DATETIME_FORMAT)
        except ValueError:
            pass

        # 全部解析失败
        return ""

    def focusOutEvent(self, event):
        # 失去焦点自动格式化修正输入内容
        raw = self.text().strip()
        if not raw:
            super().focusOutEvent(event)
            return
        std = self._parse_any_input(raw)
        if std:
            self.setText(std)
        else:
            # 格式错误直接清空
            self.clear()
        super().focusOutEvent(event)

    def focusInEvent(self, event):
        # 空白框点击时自动填入当前时间
        if not self.text().strip():
            now = datetime.now().strftime(DATETIME_FORMAT)
            self.setText(now)
        super().focusInEvent(event)