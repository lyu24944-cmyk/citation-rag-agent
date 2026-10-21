"""入库与作答。回答只引用检索到的块。"""

from __future__ import annotations

from citation_rag.config import settings
from citation_rag.models import AskResult, Citation, DocumentIn, IngestResult
from citation_rag.store import Store
from citation_rag.text import chunk_text

ABSTAIN_ANSWER = "知识库里没有足够依据回答这个问题。"


def ingest(document: DocumentIn, store: Store) -> IngestResult:
    """切块、向量化并覆盖写入。空正文得到 0 块。"""
    pieces = chunk_text(document.body, settings.chunk_size, settings.chunk_overlap)
    count = store.replace_document(document.doc_id, document.title, pieces)
    return IngestResult(doc_id=document.doc_id, chunk_count=count)


def ask(
    question: str,
    store: Store,
    *,
    top_k: int | None = None,
    min_score: float | None = None,
) -> AskResult:
    """有命中才摘录原文；否则明确说没有依据，且不带引用。"""
    text = (question or "").strip()
    if not text:
        return AskResult(question=text, answer=ABSTAIN_ANSWER, citations=[], abstained=True)

    hits = store.search(
        text,
        top_k=top_k if top_k is not None else settings.top_k,
        min_score=settings.min_score if min_score is None else min_score,
        score_margin=settings.score_margin,
    )
    if not hits:
        return AskResult(question=text, answer=ABSTAIN_ANSWER, citations=[], abstained=True)

    lines: list[str] = []
    citations: list[Citation] = []
    for hit in hits:
        lines.append(f"根据「{hit.title}」（{hit.chunk_id}）：{hit.text}")
        citations.append(
            Citation(
                chunk_id=hit.chunk_id,
                doc_id=hit.doc_id,
                title=hit.title,
                excerpt=hit.text,
                score=hit.score,
            )
        )
    return AskResult(question=text, answer="\n".join(lines), citations=citations, abstained=False)
