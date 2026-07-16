# utils/logger.py
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from config import LOG_DIR

# 日志级别映射
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# 全局可修改日志级别
GLOBAL_LOG_LEVEL = "INFO"

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件名按天切割
log_file_name = os.path.join(LOG_DIR, f"plush_system_{datetime.now().strftime('%Y%m%d')}.log")

# 创建logger单例
def get_logger(name: str = "plush_app") -> logging.Logger:
    logger = logging.getLogger(name)
    # 避免重复添加handler
    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL_MAP[GLOBAL_LOG_LEVEL])
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 1. 文件处理器：按天分割日志，保留30天
    file_handler = TimedRotatingFileHandler(
        filename=log_file_name,
        when="D",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 2. 控制台输出处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 对外暴露默认日志对象
app_log = get_logger()

if __name__ == "__main__":
    # 测试日志
    app_log.debug("调试信息")
    app_log.info("普通信息")
    app_log.warning("警告提示")
    app_log.error("错误信息")
