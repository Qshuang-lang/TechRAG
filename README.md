# TechRAG 企业 IT 知识问答系统

基于 EduRAG 架构改造的 toB 技术问答项目：IT 技术文档问答（MySQL / Docker / Kubernetes / Linux 等）。
问答流水线：`Greeting → FAQ(TF-IDF) → RAG(Milvus) → 联网(SerpAPI) → Fallback`

## 技术栈

FastAPI + Jinja2 + MySQL + Milvus + DashScope(OpenAI 兼容) + Typer CLI

## 目录结构

```
rag/
├── .env                 # 配置（当前 MySQL/Milvus 未启动，Key 待填）
├── app.py               # FastAPI 入口
├── run.py               # 一键启动
├── cli.py               # Typer CLI
├── pipeline.py          # 问答流水线
├── routes.py            # /api/chat 等路由
├── config.py / logger.py / prompts.py
├── db/                  # SQLAlchemy 模型与会话（FAQ、RAG 父子分块、会话消息）
├── clients/             # LLM / Embedding / Milvus / Elasticsearch 客户端
├── services/            # greeting / faq / rag / web_search / fallback
├── utils/               # 分块、分词预处理
├── commands/            # init-db / init-milvus / ingest-faq / ingest-rag / ask
├── scripts/             # 官方文档与 SO 问答抓取脚本（数据准备用）
├── templates/index.html # Web 对话页
└── storage/data/        # 数据目录（当前留空，等待后续加入公开数据）
```

## 使用步骤

1. 安装依赖：`.venv\Scripts\python.exe -m pip install -r requirements.txt`
2. 配置 `.env`：填写 OPENAI_API_KEY / SERPAPI_KEY，MySQL 与 Milvus 地址
3. 启动 MySQL 与 Milvus 后初始化：
   - `.venv\Scripts\python.exe cli.py init-db`
   - `.venv\Scripts\python.exe cli.py init-milvus`
4. 准备数据后导入：
   - `.venv\Scripts\python.exe cli.py ingest-faq --source storage/data/faq`
   - `.venv\Scripts\python.exe cli.py ingest-rag --source storage/data/rag_docs`
5. 启动 Web：`.venv\Scripts\python.exe run.py`，访问 http://127.0.0.1:8000

命令行测试：`.venv\Scripts\python.exe cli.py ask "MySQL 连接报 2003 错误怎么办"`

## 当前状态

- [x] 虚拟环境 + 依赖安装
- [x] 代码骨架实现
- [ ] MySQL / Milvus 启动（待用户提供启动方式）
- [ ] 公开数据获取与入库（数据留空待填）
