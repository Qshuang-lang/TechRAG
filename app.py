"""FastAPI 入口：路由 + 启动。"""
import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import config
from logger import get_logger
from routes import router

logger = get_logger("app")

app = FastAPI(title="TechRAG 企业 IT 知识问答系统", version="0.1.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

app.include_router(router)


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


def main():
    import uvicorn

    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)
