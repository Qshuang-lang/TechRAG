"""路由：聊天接口与会话管理。"""
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from db.session import SessionLocal
from db.models import Conversation, Message
from logger import get_logger
from pipeline import ask

logger = get_logger("routes")
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    conversation_id: int | None = None
    enable_rag: bool = True
    enable_web: bool = True


@router.post("/chat")
def chat(req: ChatRequest):
    result = ask(req.question, enable_rag=req.enable_rag, enable_web=req.enable_web)

    db = SessionLocal()
    try:
        # 会话：没有就新建；传入了但不存在则忽略并新建
        conv_id = req.conversation_id
        if conv_id is None or db.get(Conversation, conv_id) is None:
            conv = Conversation(title=req.question[:20] or "新会话")
            db.add(conv)
            db.flush()
            conv_id = conv.id

        db.add(Message(conversation_id=conv_id, role="user", content=req.question, stage=result["stage"]))
        db.add(Message(conversation_id=conv_id, role="assistant", content=result["answer"], stage=result["stage"]))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning("消息入库失败（MySQL 未启动时忽略）: %s", e)
        conv_id = req.conversation_id
    finally:
        db.close()

    return {
        "answer": result["answer"],
        "stage": result["stage"],
        "detail": result["detail"],
        "conversation_id": conv_id,
        "ts": datetime.now().isoformat(),
    }


@router.get("/conversations")
def list_conversations():
    db = SessionLocal()
    try:
        rows = db.query(Conversation).order_by(Conversation.created_at.desc()).limit(50).all()
        return [{"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()} for c in rows]
    except Exception as e:
        logger.warning("会话列表读取失败: %s", e)
        return []
    finally:
        db.close()


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: int):
    db = SessionLocal()
    try:
        conv = db.get(Conversation, conversation_id)
        if conv is None:
            raise HTTPException(status_code=404, detail="会话不存在")
        rows = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .all()
        )
        return {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "messages": [
                {"id": m.id, "role": m.role, "content": m.content, "stage": m.stage,
                 "created_at": m.created_at.isoformat()}
                for m in rows
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("会话消息读取失败: %s", e)
        raise HTTPException(status_code=500, detail="会话消息读取失败")
    finally:
        db.close()


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int):
    db = SessionLocal()
    try:
        conv = db.get(Conversation, conversation_id)
        if conv is None:
            raise HTTPException(status_code=404, detail="会话不存在")
        # 级联删除消息（MySQL 外键默认无 ON DELETE CASCADE，需显式删除）
        db.query(Message).filter(Message.conversation_id == conversation_id).delete(synchronize_session=False)
        db.delete(conv)
        db.commit()
        return {"ok": True, "id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.warning("会话删除失败: %s", e)
        raise HTTPException(status_code=500, detail="会话删除失败")
    finally:
        db.close()
