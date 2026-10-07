"""Greeting 阶段：问候语匹配。"""
from prompts import GREETING_QUESTIONS


def is_greeting(question: str) -> bool:
    q = question.strip().lower()
    for key in GREETING_QUESTIONS:
        if key.lower() in q:
            return True
    return False


def greeting_answer(question: str) -> str:
    q = question.strip().lower()
    for key, answer in GREETING_QUESTIONS.items():
        if key.lower() in q:
            return answer
    return GREETING_QUESTIONS["你好"]
