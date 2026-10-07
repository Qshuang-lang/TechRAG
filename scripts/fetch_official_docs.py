"""官方文档抓取脚本（数据准备阶段使用）。

用法（先 pip install requests beautifulsoup4）：
  python scripts/fetch_official_docs.py --url https://example.com/docs --out storage/data/rag_docs/example.txt

说明：部分站点有反爬/JS 渲染，可后续用 selenium 或直接下载官方离线包。
"""
import argparse
import os
import sys
import time

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fetch_page(url: str, out_dir: str, filename: str | None = None):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TechRAG"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text("\n")
    name = filename or url.rstrip("/").split("/")[-1].replace(".", "_") or "doc"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(text)
    print(f"已保存: {path} ({len(text)} 字符)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", default="storage/data/rag_docs")
    args = parser.parse_args()
    fetch_page(args.url, args.out)
    time.sleep(1)
