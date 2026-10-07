"""初始化 Milvus 集合。"""
from clients.milvus import milvus
from logger import get_logger

logger = get_logger("commands.init_milvus")


def run():
    try:
        if milvus.has_collection():
            logger.info("Milvus 集合 %s 已存在，跳过创建", milvus.collection)
        else:
            milvus.create_collection()
            logger.info("Milvus 集合 %s 创建成功", milvus.collection)
    except Exception as e:
        logger.error("Milvus 初始化失败（请确认 Milvus 已启动并修改 .env 配置）: %s", e)
        raise SystemExit(1)
