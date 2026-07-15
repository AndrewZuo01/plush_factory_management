import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel, QMessageBox
)

# 数据库工具类：封装SQLite操作
class SqliteDB:
    def __init__(self, db_file="data.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        # 初始化数据表，不存在则创建
        self.create_table()

    def create_table(self):
        # 用户表：自增id、姓名、年龄
        sql = """
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER
        )
        """
        self.cursor.execute(sql)
        self.conn.commit()

    # 查询所有数据
    def query_all(self):
        self.cursor.execute("SELECT id, name, age FROM user")
        return self.cursor.fetchall()

    # 新增数据
    def add(self, name, age):
        self.cursor.execute("INSERT INTO user(name, age) VALUES (?, ?)", (name, age))
        self.conn.commit()

    # 修改数据
    def update(self, uid, name, age):
        self.cursor.execute("UPDATE user SET name=?, age=? WHERE id=?", (name, age, uid))
        self.conn.commit()

    # 删除单条
    def delete(self, uid):
        self.cursor.execute("DELETE FROM user WHERE id=?", (uid,))
        self.conn.commit()

    # 清空整张表
    def clear_all(self):
        self.cursor.execute("DELETE FROM user")
        self.conn.commit()
        # 重置自增主键
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='user'")
        self.conn.commit()

    def close(self):
        self.conn.close()

# 主界面窗口
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 + SQLite 本地数据管理")
        self.resize(600, 450)
        self.db = SqliteDB()

        # 中心控件与布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 输入行：姓名 + 年龄
        input_layout = QHBoxLayout()
        self.label_name = QLabel("姓名：")
        self.edit_name = QLineEdit()
        self.label_age = QLabel("年龄：")
        self.edit_age = QLineEdit()
        input_layout.addWidget(self.label_name)
        input_layout.addWidget(self.edit_name)
        input_layout.addWidget(self.label_age)
        input_layout.addWidget(self.edit_age)
        main_layout.addLayout(input_layout)

        # 按钮栏
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("新增")
        self.btn_edit = QPushButton("修改选中")
        self.btn_del = QPushButton("删除选中")
        self.btn_refresh = QPushButton("刷新列表")
        self.btn_clear = QPushButton("清空全部")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_del)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_clear)
        main_layout.addLayout(btn_layout)

        # 表格控件
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "姓名", "年龄"])
        main_layout.addWidget(self.table)

        # 绑定信号槽
        self.btn_add.clicked.connect(self.add_item)
        self.btn_edit.clicked.connect(self.edit_item)
        self.btn_del.clicked.connect(self.del_item)
        self.btn_refresh.clicked.connect(self.load_table)
        self.btn_clear.clicked.connect(self.clear_db)
        # 表格点击回填数据到输入框
        self.table.cellClicked.connect(self.fill_input)

        # 启动加载一次数据
        self.load_table()
        # 记录当前选中行ID
        self.current_id = None

    # 加载数据库数据到表格
    def load_table(self):
        self.table.setRowCount(0)
        data_list = self.db.query_all()
        for row_idx, row_data in enumerate(data_list):
            self.table.insertRow(row_idx)
            for col_idx, val in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))
        self.current_id = None

    # 点击表格行，把数据填入输入框
    def fill_input(self, row, col):
        id_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        age_item = self.table.item(row, 2)
        if not all([id_item, name_item, age_item]):
            return
        self.current_id = int(id_item.text())
        self.edit_name.setText(name_item.text())
        self.edit_age.setText(age_item.text())

    # 新增
    def add_item(self):
        name = self.edit_name.text().strip()
        age_str = self.edit_age.text().strip()
        if not name or not age_str:
            QMessageBox.warning(self, "提示", "姓名和年龄不能为空")
            return
        try:
            age = int(age_str)
        except ValueError:
            QMessageBox.warning(self, "提示", "年龄必须是数字")
            return
        self.db.add(name, age)
        self.edit_name.clear()
        self.edit_age.clear()
        self.load_table()

    # 修改选中条目
    def edit_item(self):
        if self.current_id is None:
            QMessageBox.information(self, "提示", "请先在表格点击选中一行数据")
            return
        name = self.edit_name.text().strip()
        age_str = self.edit_age.text().strip()
        if not name or not age_str:
            QMessageBox.warning(self, "提示", "姓名和年龄不能为空")
            return
        try:
            age = int(age_str)
        except ValueError:
            QMessageBox.warning(self, "提示", "年龄必须是数字")
            return
        self.db.update(self.current_id, name, age)
        self.load_table()

    # 删除选中
    def del_item(self):
        if self.current_id is None:
            QMessageBox.information(self, "提示", "请先选中一行")
            return
        ret = QMessageBox.question(self, "确认", "确定要删除该条数据吗？")
        if ret == QMessageBox.Yes:
            self.db.delete(self.current_id)
            self.edit_name.clear()
            self.edit_age.clear()
            self.current_id = None
            self.load_table()

    # 清空整张表
    def clear_db(self):
        ret = QMessageBox.question(self, "警告", "将删除所有数据，不可恢复，确认？")
        if ret == QMessageBox.Yes:
            self.db.clear_all()
            self.edit_name.clear()
            self.edit_age.clear()
            self.current_id = None
            self.load_table()

    # 窗口关闭时关闭数据库连接
    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())