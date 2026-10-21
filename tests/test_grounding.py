"""引用必须来自命中的原文，空问题和闲聊不得编造。"""

from citation_rag.models import DocumentIn
from citation_rag.qa import ABSTAIN_ANSWER, ask, ingest
from citation_rag.store import Store


def test_excerpt_is_stored_text(store: Store) -> None:
    ingest(
        DocumentIn(
            doc_id="doc-delete",
            title="账号注销",
            body="注销需邮件确认，并有 7 天冷静期。",
        ),
        store,
    )
    result = ask("注销账号有冷静期吗", store)
    assert result.abstained is False
    assert result.citations
    for item in result.citations:
        stored = store.get(item.chunk_id)
        assert stored is not None
        assert item.excerpt == stored.text
        assert item.excerpt in result.answer
        assert item.chunk_id.startswith(item.doc_id)


def test_blank_question_abstains(store: Store) -> None:
    ingest(DocumentIn(doc_id="doc-refund", title="退款政策", body="14 天内退款。政策编号 REF-14。"), store)
    result = ask("   ", store)
    assert result.abstained is True
    assert result.citations == []
    assert result.answer == ABSTAIN_ANSWER
    assert "REF-14" not in result.answer


def test_smalltalk_does_not_mention_policy(store: Store) -> None:
    ingest(
        DocumentIn(doc_id="doc-refund", title="退款政策", body="未使用订阅可在 14 天内退款。政策编号 REF-14。"),
        store,
    )
    result = ask("hello just saying hi", store)
    assert result.citations == []
    assert "REF-14" not in result.answer
    assert "退款" not in result.answer
