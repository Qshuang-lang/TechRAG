"""数据库会话与初始化。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import config
from db.base import Base

engine = create_engine(config.mysql_url, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """按模型建表（开发期用 create_all；生产建议改用 alembic 迁移）。"""
    Base.metadata.create_all(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
