# service/process_stat_service.py
from statistics import mean
from database.models.quote_model import get_all_process
from database.models.schedule_model import get_all_schedule_list
from utils import app_log


def remove_min_max(data_list: list[float]) -> list[float]:
    """剔除一组数据的最小值、最大值各一个，返回剩余数组"""
    if len(data_list) <= 2:
        # 数据不足3条，无法剔除极值，直接原数据返回
        return data_list
    sorted_data = sorted(data_list)
    # 去掉最小第一条、最大最后一条
    return sorted_data[1:-1]


def calc_process_stat_data() -> list[dict]:
    """
    全工序统计分析
    返回每道工序：工序名、标准计划工期、剔除极值后平均实际工期、平均工期差值
    """
    # 1. 获取所有基础工序（标准计划工期）
    all_process = get_all_process()
    # 2. 获取全部排期记录
    all_schedule = get_all_schedule_list()

    # 按工序ID分组存储实际工期
    process_time_group = {}
    for p in all_process:
        process_time_group[p["id"]] = {
            "process_name": p["process_name"],
            "std_plan_price": p["default_price"],
            "actual_day_list": []
        }

    # 遍历所有排期，计算有效实际工期
    for item in all_schedule:
        pid = item["process_id"]
        plan_start = item["plan_start"]
        plan_end = item["plan_end"]
        actual_start = item["actual_start"]
        actual_end = item["actual_end"]

        # 跳过无完整实际时间的数据
        if not actual_start or not actual_end:
            continue

        # 计算本条实际工期天数（复用已有计算逻辑）
        from service.schedule_track_service import calc_duration_days
        actual_days = calc_duration_days(actual_start, actual_end)
        if actual_days <= 0:
            continue
        process_time_group[pid]["actual_day_list"].append(actual_days)

    # 计算每道工序统计值
    stat_result = []
    for pid, data in process_time_group.items():
        day_list = data["actual_day_list"]
        filtered_days = remove_min_max(day_list)

        # 均值
        if filtered_days:
            avg_actual = round(mean(filtered_days), 2)
            raw_avg = round(mean(day_list), 2)
        else:
            avg_actual = 0.00
            raw_avg = 0.00

        # 标准计划工期（取该工序所有排期平均计划工期）
        plan_day_all = []
        for s in all_schedule:
            if s["process_id"] == pid and s["plan_start"] and s["plan_end"]:
                d = calc_duration_days(s["plan_start"], s["plan_end"])
                if d > 0:
                    plan_day_all.append(d)
        std_plan_avg = round(mean(plan_day_all), 2) if plan_day_all else 0.00

        # 平均差值：实际平均 - 计划平均
        diff_avg = round(avg_actual - std_plan_avg, 2)

        stat_result.append({
            "process_name": data["process_name"],
            "std_plan_days": std_plan_avg,
            "origin_data_count": len(day_list),
            "filter_data_count": len(filtered_days),
            "avg_actual_days": avg_actual,
            "avg_diff_days": diff_avg
        })
    app_log.info("工序统计数据计算完成")
    return stat_result
