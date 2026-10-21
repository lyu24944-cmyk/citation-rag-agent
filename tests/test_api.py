"""HTTP 路径与库函数一致。"""

from fastapi.testclient import TestClient

from citation_rag.api.main import create_app
from citation_rag.store import Store


def test_ingest_then_ask_then_abstain(tmp_path) -> None:
    client = TestClient(create_app(Store(tmp_path / "rag.db")))
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["chunks"] == 0

    created = client.post(
        "/documents",
        json={
            "doc_id": "doc-refund",
            "title": "退款政策",
            "body": "未使用订阅可在 14 天内退款。政策编号 REF-14。",
        },
    )
    assert created.status_code == 200
    assert created.json()["chunk_count"] == 1

    answered = client.post("/ask", json={"question": "几天内可以退款"})
    body = answered.json()
    assert answered.status_code == 200
    assert body["abstained"] is False
    assert body["citations"][0]["doc_id"] == "doc-refund"

    weather = client.post("/ask", json={"question": "今天天气怎么样"})
    assert weather.json()["abstained"] is True
    assert weather.json()["citations"] == []
