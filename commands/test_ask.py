"""命令行测试问答（无需启动 Web 服务）。"""
import typer

from pipeline import ask


def run(question: str):
    result = ask(question)
    print(f"\n[阶段] {result['stage']} | {result['detail']}")
    print(f"[回答] {result['answer']}\n")
