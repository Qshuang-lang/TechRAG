"""导入 FAQ 题库（待数据准备后使用）。"""
import json
import os

import typer

from db.session import SessionLocal
from db.models import Faq
from logger import get_logger
from utils.preprocess import faq_tokens

logger = get_logger("commands.ingest_faq")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "data")


def run(source: str = ""):
    """source: JSON 文件路径或目录；文件形如 [{category, question, answer}, ...]。"""
    db = SessionLocal()
    count = 0
    try:
        if not source:
            source = os.path.join(DATA_DIR, "faq")
            os.makedirs(source, exist_ok=True)
            logger.info("未指定 source，使用默认目录 %s（当前为空则跳过）", source)

        if os.path.isdir(source):
            files = [f for f in os.listdir(source) if f.endswith(".json")]
        elif os.path.isfile(source):
            files = [os.path.basename(source)]
            source = os.path.dirname(source)
        else:
            logger.error("路径不存在: %s", source)
            raise SystemExit(1)

        for fname in files:
            path = os.path.join(source, fname)
            with open(path, encoding="utf-8") as fp:
                items = json.load(fp)
            for it in items:
                db.add(Faq(category=it.get("category", ""), question=it["question"], answer=it["answer"]))
                count += 1
        db.commit()
        logger.info("FAQ 导入完成，共 %d 条", count)
    except Exception as e:
        db.rollback()
        logger.error("FAQ 导入失败: %s", e)
        raise SystemExit(1)
    finally:
        db.close()
