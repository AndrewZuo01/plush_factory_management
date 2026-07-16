import os
import sys

# ===================== 项目根目录定位 =====================
# 本文件路径：config/path_cfg.py
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 适配PyInstaller打包后exe运行路径
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS

# ===================== 一级目录路径 =====================
# 配置文件夹
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# 数据库相关
DB_ROOT_DIR = os.path.join(BASE_DIR, "database")
DB_DATA_DIR = os.path.join(DB_ROOT_DIR, "data")
DB_FILE_PATH = os.path.join(DB_DATA_DIR, "plush_db.sqlite")

# 业务逻辑层
SERVICE_DIR = os.path.join(BASE_DIR, "service")

# 界面视图层
VIEW_DIR = os.path.join(BASE_DIR, "view")
WIDGETS_DIR = os.path.join(VIEW_DIR, "widgets")
PAGES_DIR = os.path.join(VIEW_DIR, "pages")

# 工具类
UTILS_DIR = os.path.join(BASE_DIR, "utils")

# 静态资源：图片、图标、样式、字体
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TOY_IMG_DIR = os.path.join(ASSETS_DIR, "toy_img")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
STYLE_DIR = os.path.join(ASSETS_DIR, "qss")
QSS_FILE_PATH = os.path.join(STYLE_DIR, "style.qss")

# 运行时生成文件存放目录
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
LOG_DIR = os.path.join(STORAGE_DIR, "runtime_logs")
BACKUP_DIR = os.path.join(STORAGE_DIR, "db_backup")
EXPORT_DIR = os.path.join(STORAGE_DIR, "exports")
ATTACH_DIR = os.path.join(STORAGE_DIR, "attachments")
TEMP_DIR = os.path.join(STORAGE_DIR, "temp")

# 插件与测试（预留）
PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

# ===================== 所有需要自动创建的文件夹列表 =====================
AUTO_CREATE_FOLDERS = [
    DB_DATA_DIR,
    LOG_DIR,
    BACKUP_DIR,
    EXPORT_DIR,
    ATTACH_DIR,
    TEMP_DIR,
    TOY_IMG_DIR,
    ICONS_DIR,
    STYLE_DIR,
]

# ===================== 初始化：不存在则自动新建目录 =====================
def init_project_folders():
    """程序启动时调用，批量创建全部必要文件夹"""
    for folder_path in AUTO_CREATE_FOLDERS:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

# 项目启动自动执行一次建文件夹
init_project_folders()

if __name__ == "__main__":
    # 单独运行此文件可打印所有路径用于调试
    print("项目根目录:", BASE_DIR)
    print("数据库文件路径:", DB_FILE_PATH)
    print("日志目录:", LOG_DIR)
    print("报价导出目录:", EXPORT_DIR)
