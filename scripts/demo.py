"""把三篇样例文档入库，并各问一次相关和无关的问题。"""

from citation_rag.config import resolve_db_path
from citation_rag.models import DocumentIn
from citation_rag.qa import ask, ingest
from citation_rag.store import Store

DOCUMENTS = [
    DocumentIn(
        doc_id="doc-refund",
        title="退款政策",
        body="未使用订阅可在 14 天内退款。政策编号 REF-14。",
    ),
    DocumentIn(
        doc_id="doc-password",
        title="密码重置",
        body="用户可通过 /settings/security 重置密码。切勿在对话中索要当前密码。",
    ),
    DocumentIn(
        doc_id="doc-delete",
        title="账号注销",
        body="注销需邮件确认，并有 7 天冷静期。",
    ),
]

QUESTIONS = [
    "订阅未使用，几天内可以退款？",
    "怎么重置密码？",
    "注销账号有冷静期吗？",
    "今天天气怎么样",
]


def main() -> None:
    store = Store(resolve_db_path())
    for document in DOCUMENTS:
        result = ingest(document, store)
        print(f"ingest {result.doc_id} chunks={result.chunk_count}")
    for question in QUESTIONS:
        answer = ask(question, store)
        cited = ",".join(item.chunk_id for item in answer.citations) or "-"
        print(f"Q {question}")
        print(f"  abstained={answer.abstained} citations={cited}")
        print(f"  {answer.answer}")


if __name__ == "__main__":
    main()
