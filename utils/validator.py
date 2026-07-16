# utils/validator.py
from datetime import datetime
from config import PRICE_DECIMAL_PLACES, MIN_PRICE_VALUE
from utils.logger import app_log


def is_valid_price(num: float | str) -> tuple[bool, float | None, str]:
    """
    校验金额是否合法：非空、数字、大于等于最小值、保留指定小数位
    :param num: 输入值
    :return: (是否合法, 格式化后数值, 错误提示文案)
    """
    try:
        val = float(num)
    except (ValueError, TypeError):
        return False, None, "请输入有效的数字金额"

    if val < MIN_PRICE_VALUE:
        return False, None, f"金额不能小于 {MIN_PRICE_VALUE}"

    # 强制四舍五入保留配置规定小数位数
    formatted = round(val, PRICE_DECIMAL_PLACES)
    return True, formatted, ""


def is_time_range_valid(start_str: str, end_str: str, fmt: str = "%Y-%m-%d %H:%M") -> tuple[bool, str]:
    """
    校验计划/实际起止时间：结束时间不能早于开始时间
    :param start_str: 开始时间字符串
    :param end_str: 结束时间字符串
    :param fmt: 时间格式
    :return: (是否合法, 错误信息)
    """
    if not start_str.strip() or not end_str.strip():
        return False, "开始时间与结束时间不能为空"
    try:
        start_dt = datetime.strptime(start_str, fmt)
        end_dt = datetime.strptime(end_str, fmt)
    except ValueError:
        return False, f"时间格式错误，请按照 {fmt} 填写"

    if end_dt < start_dt:
        return False, "结束时间不能早于开始时间"
    return True, ""


def not_empty(text: str, field_name: str = "内容") -> tuple[bool, str]:
    """通用非空校验"""
    if not text or not str(text).strip():
        return False, f"{field_name}不能为空"
    return True, ""


def quote_no_format_check(quote_no: str) -> tuple[bool, str]:
    """简单校验报价单号基础格式（可按需扩展正则）"""
    if not quote_no.startswith("Q"):
        return False, "报价单号必须以Q开头"
    if len(quote_no) < 5:
        return False, "报价单号长度过短"
    return True, ""


def log_validate_fail(func_name: str, msg: str):
    """统一记录校验失败日志"""
    app_log.warning(f"【校验失败】{func_name}：{msg}")
