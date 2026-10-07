"""Stack Overflow 公开问答抓取脚本（数据准备阶段使用，遵守 robots/API 条款）。

用法（需 pip install requests beautifulsoup4）：
  python scripts/fetch_so_qa.py --tag mysql --pages 3 --out storage/data/faq/so_mysql.json

说明：优先使用 Stack Exchange API（配额 300 次/天）。先按票数拉问题列表，
再批量拉取每题最高票答案正文，输出 [{category, question, answer, link}]，
可直接 ingest-faq 入库。
"""
import argparse
import json
import os
import sys
import time

import requests
from bs4 import BeautifulSoup

SEARCH_API = "https://api.stackexchange.com/2.3/search/advanced"
ANSWERS_API = "https://api.stackexchange.com/2.3/questions/{ids}/answers"
SITE = "stackoverflow"


def fetch_questions(tag: str, pages: int) -> list[dict]:
    items_all = []
    for page in range(1, pages + 1):
        params = {
            "site": SITE,
            "tagged": tag,
            "pagesize": 50,
            "page": page,
            "order": "desc",
            "sort": "votes",
            "filter": "withbody",
        }
        resp = requests.get(SEARCH_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        items_all.extend(data.get("items", []))
        print(f"  第 {page} 页: 获取 {len(data.get('items', []))} 个问题，剩余配额 {data.get('quota_remaining', '?')}")
        time.sleep(1)
    return items_all


def fetch_answers(question_ids: list[int]) -> dict[int, str]:
    """批量拉取每题最高票答案正文，返回 {question_id: answer_text}。"""
    result = {}
    for i in range(0, len(question_ids), 100):
        batch = question_ids[i:i + 100]
        ids = ";".join(str(qid) for qid in batch)
        params = {"site": SITE, "order": "desc", "sort": "votes", "filter": "withbody", "pagesize": 100}
        resp = requests.get(ANSWERS_API.format(ids=ids), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for ans in data.get("items", []):
            qid = ans.get("question_id")
            if qid is None or qid in result:
                continue
            body = html_to_text(ans.get("body", ""))
            if body:
                result[qid] = body
        print(f"  答案批次: 获取 {len(data.get('items', []))} 条答案，剩余配额 {data.get('quota_remaining', '?')}")
        time.sleep(1)
    return result


def html_to_text(html: str) -> str:
    """HTML 正文转纯文本，代码块保留 ``` 包裹。"""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["pre", "code"]):
        tag.replace_with("```" + tag.get_text() + "```")
    return soup.get_text("\n").strip()


def fetch_qa(tag: str, pages: int = 2) -> list[dict]:
    questions = fetch_questions(tag, pages)
    qids = [it["question_id"] for it in questions if it.get("title") and it.get("question_id")]
    answers = fetch_answers(qids) if qids else {}
    result = []
    for it in questions:
        title = it.get("title", "")
        if not title:
            continue
        qid = it.get("question_id")
        result.append(
            {
                "category": tag,
                "question": title,
                "answer": answers.get(qid, ""),
                "link": it.get("link", ""),
            }
        )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="技术标签，如 mysql/docker/kubernetes")
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--out", default="storage/data/faq/so.json")
    args = parser.parse_args()

    data = fetch_qa(args.tag, args.pages)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    print(f"已保存 {len(data)} 条问答: {args.out}")
