"""业务模型：FAQ 题库、RAG 父子分块、会话与消息。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from db.base import Base


class Faq(Base):
    """FAQ 题库（短问短答，存 MySQL）。"""

    __tablename__ = "faq"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(64), default="")          # 技术分类
    question = Column(Text, nullable=False)            # 问题
    answer = Column(Text, nullable=False)              # 答案
    tokens = Column(Text, default="")                  # 分词结果（空格分隔，入库时写入）
    created_at = Column(DateTime, default=datetime.now)


class RagChunk(Base):
    """RAG 父块（原文粒度，入库 MySQL）。"""

    __tablename__ = "rag_chunk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(MEDIUMTEXT, nullable=False)       # 父块原文
    source = Column(String(255), default="")           # 来源（文档名/URL）
    created_at = Column(DateTime, default=datetime.now)


class RagChildChunk(Base):
    """RAG 子块（检索粒度，向量写入 Milvus）。"""

    __tablename__ = "rag_child_chunk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("rag_chunk.id"), index=True)
    content = Column(Text, nullable=False)             # 子块内容
    created_at = Column(DateTime, default=datetime.now)


class Conversation(Base):
    """会话。"""

    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), default="新会话")
    created_at = Column(DateTime, default=datetime.now)


class Message(Base):
    """会话消息。"""

    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), index=True)
    role = Column(String(16), nullable=False)          # user / assistant
    content = Column(Text, nullable=False)
    stage = Column(String(16), default="")             # greeting/faq/rag/web/fallback
    created_at = Column(DateTime, default=datetime.now)
