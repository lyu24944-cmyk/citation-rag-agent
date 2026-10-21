"""检索：相关问题命中对应文档，无关问题为空。"""

from citation_rag.models import DocumentIn
from citation_rag.qa import ask, ingest
from citation_rag.store import Store


def _load(store: Store) -> None:
    ingest(
        DocumentIn(
            doc_id="doc-refund",
            title="退款政策",
            body="未使用订阅可在 14 天内退款。政策编号 REF-14。",
        ),
        store,
    )
    ingest(
        DocumentIn(
            doc_id="doc-password",
            title="密码重置",
            body="用户可通过 /settings/security 重置密码。切勿在对话中索要当前密码。",
        ),
        store,
    )


def test_refund_question_cites_refund_doc(store: Store) -> None:
    _load(store)
    result = ask("订阅未使用，几天内可以退款？", store)
    assert result.abstained is False
    assert any(item.doc_id == "doc-refund" for item in result.citations)


def test_password_question_cites_password_doc(store: Store) -> None:
    _load(store)
    result = ask("怎么重置密码？", store)
    assert any(item.doc_id == "doc-password" for item in result.citations)


def test_unrelated_question_has_no_hits(store: Store) -> None:
    _load(store)
    result = ask("今天天气怎么样", store)
    assert result.abstained is True
    assert result.citations == []


def test_reopen_store_still_finds_document(tmp_path) -> None:
    path = tmp_path / "rag.db"
    first = Store(path)
    ingest(
        DocumentIn(doc_id="doc-refund", title="退款政策", body="未使用订阅可在 14 天内退款。"),
        first,
    )
    second = Store(path)
    result = ask("几天内可以退款", second)
    assert any(item.doc_id == "doc-refund" for item in result.citations)


def test_reingest_replaces_chunks(store: Store) -> None:
    ingest(DocumentIn(doc_id="doc-refund", title="退款政策", body="旧正文" * 100), store)
    first_count = store.count()
    ingest(DocumentIn(doc_id="doc-refund", title="退款政策", body="未使用订阅可在 14 天内退款。"), store)
    assert first_count > 1
    assert store.count() == 1
