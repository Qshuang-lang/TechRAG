"""初始化 MySQL 建表。"""
from db.session import engine, init_db
from logger import get_logger

logger = get_logger("commands.init_db")


def run():
    try:
        init_db()
        logger.info("建表完成，数据库 URL: %s", str(engine.url).replace(engine.url.password or "", "***"))
    except Exception as e:
        logger.error("建表失败（请确认 MySQL 已启动并修改 .env 配置）: %s", e)
        raise SystemExit(1)
