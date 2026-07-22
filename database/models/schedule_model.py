# database/models/schedule_model.py
from database import db
from utils import app_log

# ===================== 生产排期 Dashboard 数据库操作 =====================

def init_schedule_by_quote(quote_id: int, process_list: list):
    """
    根据报价单工序，批量初始化一套空白排期记录
    :param quote_id: 关联报价单ID
    :param process_list: 工序列表
    """
    # 先删除该报价旧排期
    del_sql = "DELETE FROM production_schedule WHERE relate_quote_id = ?"
    db.execute_sql(del_sql, (quote_id,))

    # 批量初始化空白排期
    insert_sql = """
    INSERT INTO production_schedule 
    (relate_quote_id, process_id, plan_start, plan_end, actual_start, actual_end, actual_cost, status)
    VALUES (?, ?, '', '', '', '', 0.00, '未开始')
    """
    for p in process_list:
        db.execute_sql(insert_sql, (quote_id, p["id"]))

    app_log.info(f"已为报价单{quote_id}初始化全套工序排期")

def get_schedule_by_id(schedule_id: int) -> dict | None:
    sql = "SELECT * FROM production_schedule WHERE id=?"
    row = db.query_one(sql, [schedule_id])
    return row

def get_schedule_by_quote_id(quote_id: int) -> list:
    """
    获取某报价单对应的所有工序排期数据（关联工序名称、排序）
    """
    sql = """
    SELECT 
        ps.id,
        ps.process_id,
        pd.process_name,
        ps.plan_start,
        ps.plan_end,
        ps.actual_start,
        ps.actual_end,
        ps.actual_cost,
        ps.status
    FROM production_schedule ps
    LEFT JOIN process_dict pd ON ps.process_id = pd.id
    WHERE ps.relate_quote_id = ?
    ORDER BY pd.sort ASC
    """

    return db.query_all(sql, (quote_id,))


def update_schedule_item(schedule_id: int, data: dict):
    """
    更新单条工序排期数据
    data可传：plan_start/plan_end/actual_start/actual_end/actual_cost/status
    """
    update_fields = []
    params = []

    if "plan_start" in data:
        update_fields.append("plan_start=?")
        params.append(data["plan_start"])
    if "plan_end" in data:
        update_fields.append("plan_end=?")
        params.append(data["plan_end"])
    if "actual_start" in data:
        update_fields.append("actual_start=?")
        params.append(data["actual_start"])
    if "actual_end" in data:
        update_fields.append("actual_end=?")
        params.append(data["actual_end"])
    if "actual_cost" in data:
        update_fields.append("actual_cost=?")
        params.append(data["actual_cost"])
    if "status" in data:
        update_fields.append("status=?")
        params.append(data["status"])
    if not update_fields:
        return

    sql = f"UPDATE production_schedule SET {','.join(update_fields)} WHERE id=?"
    params.append(schedule_id)
    db.execute_sql(sql, params)


def get_schedule_total_cost(quote_id: int) -> float:
    """
    统计该报价单所有工序【实际总成本】
    """
    sql = """
    SELECT SUM(actual_cost) AS total_cost 
    FROM production_schedule 
    WHERE relate_quote_id = ?
    """
    res = db.query_one(sql, (quote_id,))
    return res["total_cost"] if res["total_cost"] else 0.00


def get_all_schedule_list():
    """获取所有排期记录（全局查看）"""
    sql = """
    SELECT ps.*, pd.process_name 
    FROM production_schedule ps
    LEFT JOIN process_dict pd ON ps.process_id = pd.id
    ORDER BY ps.id DESC
    """
    return db.query_all(sql)
