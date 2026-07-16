# service/quote_calc_service.py
from typing import List, Tuple
from config import PRICE_DECIMAL_PLACES, QUOTE_NO_PREFIX
from database.models.quote_model import (
    get_all_process,
    create_quote_order,
    batch_save_quote_items,
    update_quote_total,
    get_quote_items
)
from utils import app_log, is_valid_price
import time

def calc_total_price(process_price_list: List[Tuple[int, float]]) -> float:
    """
    根据工序价格列表计算总价
    :param process_price_list: [(process_id, price), ...]
    :return: 四舍五入后总价
    """
    total = sum(price for _, price in process_price_list)
    return round(total, PRICE_DECIMAL_PLACES)

def batch_adjust_price(origin_list: List[Tuple[int, float]], ratio: float) -> List[Tuple[int, float]]:
    """
    批量整体调价
    :param origin_list: 原价格列表 [(pid, price),...]
    :param ratio: 倍率 1.1 / 0.9 ...
    :return: 新价格列表
    """
    new_list = []
    for pid, price in origin_list:
        new_price = round(price * ratio, PRICE_DECIMAL_PLACES)
        # 防止负数
        if new_price < 0:
            new_price = 0.00
        new_list.append((pid, new_price))
    app_log.info(f"批量调价完成，倍率:{ratio}")
    return new_list

def get_default_process_price_list() -> List[Tuple[int, float]]:
    """
    获取系统默认整套工序价格（新建报价初始值）
    """
    process_data = get_all_process()
    res = []
    for p in process_data:
        res.append((p["id"], p["default_price"]))
    return res

def generate_quote_no() -> str:
    """
    生成唯一报价单号: Q + 时间戳
    """
    timestamp = str(int(time.time()))[-8:]
    return f"{QUOTE_NO_PREFIX}{timestamp}"

def save_new_quote(toy_name: str, remark: str, process_price_list: List[Tuple[int, float]]) -> int:
    """
    保存全新报价单
    :param toy_name: 玩具名称
    :param remark: 备注
    :param process_price_list: 所有工序价格列表
    :return: 新报价单ID
    """
    # 1. 生成单号
    quote_no = generate_quote_no()

    # 2. 计算总价
    total = calc_total_price(process_price_list)

    # 3. 创建主单
    quote_id = create_quote_order(quote_no, toy_name, remark)

    # 4. 批量保存工序明细
    batch_save_quote_items(quote_id, process_price_list)

    # 5. 更新总价
    update_quote_total(quote_id, total)

    app_log.info(f"新报价单保存成功 ID:{quote_id} NO:{quote_no} 总价:{total}")
    return quote_id

def load_quote_process_price(quote_id: int) -> List[Tuple[int, float]]:
    """
    加载历史报价的工序价格
    :param quote_id: 报价单ID
    :return: [(pid, price), ...]
    """
    items = get_quote_items(quote_id)
    res = []
    for item in items:
        ok, price, _ = is_valid_price(item["unit_price"])
        if ok:
            res.append((item["process_id"], price))
    return res
