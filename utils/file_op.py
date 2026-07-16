# utils/file_op.py
import os
import shutil
from datetime import datetime
from config import EXPORT_DIR, BACKUP_DIR, ATTACH_DIR, TEMP_DIR, DB_FILE_PATH
from utils.logger import app_log


def make_dir_if_not_exist(folder_path: str):
    """
    单个目录不存在则创建
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        app_log.info(f"目录已自动创建: {folder_path}")


def get_new_export_filename(prefix: str = "报价单") -> str:
    """
    生成导出文件标准文件名，带时间戳
    :param prefix: 文件前缀
    :return: 完整文件路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.xlsx"
    full_path = os.path.join(EXPORT_DIR, filename)
    return full_path


def backup_sqlite_db() -> str:
    """
    备份SQLite数据库文件到备份目录，返回备份文件完整路径
    """
    make_dir_if_not_exist(BACKUP_DIR)
    if not os.path.isfile(DB_FILE_PATH):
        app_log.warning("数据库文件不存在，无法执行备份")
        return ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"plush_db_backup_{timestamp}.sqlite"
    backup_full_path = os.path.join(BACKUP_DIR, backup_name)

    try:
        shutil.copy2(DB_FILE_PATH, backup_full_path)
        app_log.info(f"数据库备份成功：{backup_full_path}")
        return backup_full_path
    except Exception as e:
        app_log.error(f"数据库备份失败: {str(e)}", exc_info=True)
        return ""


def restore_sqlite_db(backup_file_path: str) -> bool:
    """
    从指定备份文件恢复数据库
    :param backup_file_path: 备份文件绝对路径
    :return: 成功True / 失败False
    """
    if not os.path.isfile(backup_file_path):
        app_log.error(f"备份文件不存在: {backup_file_path}")
        return False
    try:
        # 覆盖原有数据库
        shutil.copy2(backup_file_path, DB_FILE_PATH)
        app_log.info(f"数据库从 {backup_file_path} 恢复完成")
        return True
    except Exception as e:
        app_log.error(f"数据库恢复失败: {str(e)}", exc_info=True)
        return False


def clear_temp_files():
    """清空临时文件夹所有内容"""
    make_dir_if_not_exist(TEMP_DIR)
    try:
        for name in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, name)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        app_log.info("临时文件清理完毕")
    except Exception as e:
        app_log.warning(f"清理临时文件出现异常: {e}")


def save_attachment(src_file_path: str, save_name: str = None) -> str:
    """
    将附件文件复制到附件存储目录
    :param src_file_path: 原文件路径
    :param save_name: 自定义保存文件名，不传则用原文件名
    :return: 保存后完整路径
    """
    make_dir_if_not_exist(ATTACH_DIR)
    if not os.path.isfile(src_file_path):
        app_log.error(f"待保存附件不存在: {src_file_path}")
        return ""

    if save_name is None:
        save_name = os.path.basename(src_file_path)
    dst_path = os.path.join(ATTACH_DIR, save_name)
    try:
        shutil.copy2(src_file_path, dst_path)
        app_log.info(f"附件已保存至: {dst_path}")
        return dst_path
    except Exception as e:
        app_log.error(f"附件保存失败: {e}", exc_info=True)
        return ""
