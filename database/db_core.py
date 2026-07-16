# database/db_core.py
import sqlite3
from config import DB_FILE_PATH
from utils import app_log


class DBConnection:
    _instance = None
    _conn = None

    def __new__(cls):
        """单例模式，全局只存在一个数据库连接"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_conn(self):
        """获取数据库连接，不存在则新建，同时开启外键"""
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(
                    DB_FILE_PATH,
                    check_same_thread=False,
                    timeout=10
                )
                # 启用外键约束
                self._conn.execute("PRAGMA foreign_keys = ON;")
                app_log.info("SQLite 数据库连接已创建")
            except Exception as e:
                app_log.error(f"数据库连接失败: {str(e)}", exc_info=True)
                raise
        return self._conn

    def close_conn(self):
        """关闭连接"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            app_log.info("数据库连接已关闭")

    def execute_sql(self, sql: str, params: tuple = ()):
        """
        执行增删改查单条SQL，自动提交
        :param sql: SQL语句
        :param params: 占位参数元组
        :return: cursor对象
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor
        except Exception as e:
            conn.rollback()
            app_log.error(f"SQL执行异常: {sql} | 参数:{params} | 错误:{str(e)}", exc_info=True)
            raise

    def query_one(self, sql: str, params: tuple = ()):
        """查询单条数据，返回字典"""
        cursor = self.execute_sql(sql, params)
        row = cursor.fetchone()
        desc = [col[0] for col in cursor.description] if cursor.description else []
        return dict(zip(desc, row)) if row else None

    def query_all(self, sql: str, params: tuple = ()):
        """查询多条数据，返回列表嵌套字典"""
        cursor = self.execute_sql(sql, params)
        rows = cursor.fetchall()
        desc = [col[0] for col in cursor.description] if cursor.description else []
        return [dict(zip(desc, item)) for item in rows]

    def insert_and_get_id(self, sql: str, params: tuple = ()) -> int:
        """插入数据并返回自增主键ID"""
        cursor = self.execute_sql(sql, params)
        return cursor.lastrowid


# 全局单例实例
db = DBConnection()