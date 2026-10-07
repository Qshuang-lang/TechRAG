此目录存放待导入的数据，暂为空。

- faq/        FAQ 题库 JSON（[{category, question, answer}]）
- rag_docs/   技术文档 TXT/MD 或 JSON（[{content, source}]）

数据准备好后放入对应子目录，用 `python cli.py ingest-faq / ingest-rag` 导入。
