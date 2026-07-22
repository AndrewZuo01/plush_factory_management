# service/schedule_track_service.py
from datetime import datetime
from config import DATETIME_FORMAT, PRICE_DECIMAL_PLACES, SCHEDULE_STATUS
from database.models.schedule_model import (
    init_schedule_by_quote,
    get_schedule_by_quote_id,
    update_schedule_item,
    get_schedule_total_cost,
    get_schedule_by_id
)
from database.models.quote_model import get_all_process
from utils import is_time_range_valid, app_log


def init_empty_schedule(quote_id: int):
    """
    根据报价单初始化一套空白排期工序
    """
    process_list = get_all_process()
    init_schedule_by_quote(quote_id, process_list)
    app_log.info(f"排期看板初始化完成 -> 报价单ID:{quote_id}")


def calc_duration_days(start_str: str, end_str: str) -> float:
    """
    计算两个时间间隔天数（支持小时、精确小数）
    空时间返回0
    """
    if not start_str or not end_str:
        return 0.0

    try:
        start = datetime.strptime(start_str, DATETIME_FORMAT)
        end = datetime.strptime(end_str, DATETIME_FORMAT)
        delta = end - start
        return round(delta.total_seconds() / 86400, 2)
    except Exception:
        return 0.0


def auto_get_process_status(plan_end: str, actual_start: str, actual_end: str) -> str:
    """
    自动判断工序状态：未开始 / 进行中 / 已完成 / 延期
    """
    # 有实际结束时间 = 已完成
    if actual_end:
        return "已完成"

    # 有实际开始时间 = 进行中
    if actual_start:
        # 判断是否超时
        now = datetime.now()
        try:
            plan_end_dt = datetime.strptime(plan_end, DATETIME_FORMAT)
            if now > plan_end_dt:
                return "延期"
        except Exception:
            pass
        return "进行中"

    # 完全没动
    return "未开始"


def save_schedule_field(schedule_id: int, data: dict):
    """
    保存单条工序排期字段 + 自动刷新状态
    """
    # 先保存用户修改的数据
    update_schedule_item(schedule_id, data)
    print("hello")

    # ✅ 修复：使用按工序ID查询单条，而不是按quote_id批量查询
    target = get_schedule_by_id(schedule_id)
    if not target:
        return

    # 自动计算状态
    new_status = auto_get_process_status(
        target["plan_end"],
        target["actual_start"],
        target["actual_end"]
    )
    
    # 按需增加：如果前端手动传入status，则不再自动覆盖状态
    # if "status" in data:
    #     return

    if new_status != target["status"]:
        update_schedule_item(schedule_id, {"status": new_status})


def get_schedule_dashboard_data(quote_id: int) -> dict:
    """
    获取整套看板数据 + 统计汇总
    返回：工序列表、总计划天数、总实际天数、总成本、是否整体延期
    """
    data_list = get_schedule_by_quote_id(quote_id)
    
    total_plan_days = 0.0
    total_actual_days = 0.0
    all_delay = False

    for item in data_list:
        # 单工序计划天数
        item["plan_days"] = calc_duration_days(item["plan_start"], item["plan_end"])
        # 单工序实际天数
        item["actual_days"] = calc_duration_days(item["actual_start"], item["actual_end"])

        total_plan_days += item["plan_days"]
        total_actual_days += item["actual_days"]

        # 任意工序延期 = 整体延期标记
        if item["status"] == "延期":
            all_delay = True

    # 总成本
    total_cost = get_schedule_total_cost(quote_id)

    return {
        "process_list": data_list,
        "total_plan_days": round(total_plan_days, 2),
        "total_actual_days": round(total_actual_days, 2),
        "total_actual_cost": round(total_cost, PRICE_DECIMAL_PLACES),
        "is_all_delay": all_delay
    }


def check_time_valid(start: str, end: str) -> tuple[bool, str]:
    """
    校验时间合法性（给UI弹窗提示用）
    """
    return is_time_range_valid(start, end, DATETIME_FORMAT)
