"""Typer CLI 入口。"""
import typer

from commands import init_db, init_milvus, ingest_faq, ingest_rag, test_ask

cli = typer.Typer(help="TechRAG 企业 IT 知识问答系统 CLI")


@cli.command("init-db")
def cmd_init_db():
    """初始化 MySQL 表结构"""
    init_db.run()


@cli.command("init-milvus")
def cmd_init_milvus():
    """创建 Milvus 集合"""
    init_milvus.run()


@cli.command("ingest-faq")
def cmd_ingest_faq(source: str = typer.Option("", help="FAQ JSON 文件或目录路径")):
    """导入 FAQ 题库"""
    ingest_faq.run(source)


@cli.command("ingest-rag")
def cmd_ingest_rag(source: str = typer.Option("", help="RAG 文档文件/目录/.json 路径")):
    """导入 RAG 文档（父块入 MySQL，子块入 Milvus）"""
    ingest_rag.run(source)


@cli.command("ask")
def cmd_ask(question: str = typer.Argument(..., help="要问的问题")):
    """命令行直接提问"""
    test_ask.run(question)


if __name__ == "__main__":
    cli()
