# database/models/quote_model.py
from database import db
from utils import app_log

# ===================== 工序字典操作 =====================
def get_all_process() -> list:
    """获取所有工序（按排序顺序）"""
    sql = """
    SELECT id, process_name, default_price, sort 
    FROM process_dict 
    ORDER BY sort ASC
    """
    return db.query_all(sql)

# ===================== 报价单主表 =====================
def create_quote_order(quote_no: str, toy_name: str, remark: str = "") -> int:
    """
    创建空报价单主记录，返回报价单ID
    """
    sql = """
    INSERT INTO quote_order (quote_no, toy_name, remark, total_price)
    VALUES (?, ?, ?, 0.00)
    """
    return db.insert_and_get_id(sql, (quote_no, toy_name, remark))

def update_quote_total(quote_id: int, total_price: float):
    """更新报价单总价格"""
    sql = "UPDATE quote_order SET total_price=? WHERE id=?"
    db.execute_sql(sql, (total_price, quote_id))

def get_quote_by_id(quote_id: int):
    """根据ID获取报价单主信息"""
    sql = "SELECT * FROM quote_order WHERE id=?"
    return db.query_one(sql, (quote_id,))

def get_all_quote_list():
    """获取所有报价单列表（倒序）"""
    sql = "SELECT * FROM quote_order ORDER BY create_time DESC"
    return db.query_all(sql)

# ===================== 报价明细（工序价格） =====================
def batch_save_quote_items(quote_id: int, process_price_list: list):
    """
    批量保存工序价格明细
    :param quote_id: 报价单ID
    :param process_price_list: [(process_id, unit_price), ...]
    """
    # 先删除旧明细
    del_sql = "DELETE FROM quote_item WHERE quote_id=?"
    db.execute_sql(del_sql, (quote_id,))

    # 插入新明细
    ins_sql = """
    INSERT INTO quote_item (quote_id, process_id, unit_price)
    VALUES (?, ?, ?)
    """
    for pid, price in process_price_list:
        db.execute_sql(ins_sql, (quote_id, pid, price))

    app_log.info(f"报价单{quote_id} 工序明细批量保存成功")

def get_quote_items(quote_id: int) -> list:
    """获取某报价单的所有工序价格明细（关联工序名称）"""
    sql = """
    SELECT 
        pd.id as process_id,
        pd.process_name,
        qi.unit_price
    FROM quote_item qi
    LEFT JOIN process_dict pd ON qi.process_id = pd.id
    WHERE qi.quote_id = ?
    ORDER BY pd.sort ASC
    """
    return db.query_all(sql, (quote_id,))
