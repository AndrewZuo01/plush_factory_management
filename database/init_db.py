# database/init_db.py
import sqlite3
from config import DB_FILE_PATH, DEFAULT_PROCESS_LIST
from utils import app_log

def init_database():
    """
    初始化数据库：建表 + 插入默认工序基础数据
    程序首次运行自动执行，重复执行不会覆盖已有数据
    """
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()
        app_log.info(f"开始初始化数据库，路径：{DB_FILE_PATH}")

        # 1. 工序字典表 process_dict
        sql_process_dict = """
        CREATE TABLE IF NOT EXISTS process_dict (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_name TEXT NOT NULL UNIQUE,
            default_price REAL NOT NULL DEFAULT 0.00,
            sort INTEGER NOT NULL DEFAULT 1
        );
        """
        cursor.execute(sql_process_dict)

        # 2. 报价单主表 quote_order
        sql_quote_order = """
        CREATE TABLE IF NOT EXISTS quote_order (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_no TEXT NOT NULL UNIQUE,
            toy_name TEXT,
            total_price REAL DEFAULT 0.00,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            remark TEXT
        );
        """
        cursor.execute(sql_quote_order)

        # 3. 报价单明细 quote_item
        sql_quote_item = """
        CREATE TABLE IF NOT EXISTS quote_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id INTEGER NOT NULL,
            process_id INTEGER NOT NULL,
            unit_price REAL DEFAULT 0.00,
            FOREIGN KEY (quote_id) REFERENCES quote_order(id) ON DELETE CASCADE,
            FOREIGN KEY (process_id) REFERENCES process_dict(id)
        );
        """
        cursor.execute(sql_quote_item)

        # 4. 生产排期看板表 production_schedule
        sql_schedule = """
        CREATE TABLE IF NOT EXISTS production_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relate_quote_id INTEGER,
            process_id INTEGER NOT NULL,
            plan_start TEXT,
            plan_end TEXT,
            actual_start TEXT,
            actual_end TEXT,
            actual_cost REAL DEFAULT 0.00,
            status TEXT DEFAULT '未开始',
            FOREIGN KEY (process_id) REFERENCES process_dict(id)
        );
        """
        cursor.execute(sql_schedule)

        # 开启外键约束
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 插入默认工序（不存在才插入，避免重复）
        for name, price, sort in DEFAULT_PROCESS_LIST:
            cursor.execute("""
                INSERT OR IGNORE INTO process_dict (process_name, default_price, sort)
                VALUES (?, ?, ?)
            """, (name, price, sort))

        conn.commit()
        app_log.info("数据表创建完成，默认工序初始化成功")

    except Exception as e:
        app_log.error("数据库初始化失败", exc_info=True)
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # 单独运行可直接初始化库
    init_database()
