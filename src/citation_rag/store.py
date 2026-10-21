"""文本块与向量落在 SQLite。规模是作品集语料，检索时全量扫描。"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from citation_rag.embed import cosine, embed


@dataclass(frozen=True)
class ChunkHit:
    """一次检索命中。"""

    chunk_id: str
    doc_id: str
    title: str
    text: str
    score: float


class Store:
    """按文档覆盖写入，按余弦相似度读出。"""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    vector TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id)")

    @contextmanager
    def _connect(self):
        """用完即关闭。Windows 上不关连接就删不掉临时库。"""
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def replace_document(self, doc_id: str, title: str, chunks: list[str]) -> int:
        """同一 doc_id 再次入库时删掉旧块，避免重复引用。"""
        with self._connect() as conn:
            conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            for index, text in enumerate(chunks):
                chunk_id = f"{doc_id}#c{index}"
                conn.execute(
                    """
                    INSERT INTO chunks (chunk_id, doc_id, title, text, vector)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (chunk_id, doc_id, title, text, json.dumps(embed(text))),
                )
        return len(chunks)

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
        return int(row["n"])

    def get(self, chunk_id: str) -> ChunkHit | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,)).fetchone()
        if row is None:
            return None
        return ChunkHit(row["chunk_id"], row["doc_id"], row["title"], row["text"], 1.0)

    def search(self, query: str, top_k: int, min_score: float) -> list[ChunkHit]:
        """分数低于门槛的块不返回。空查询直接为空。"""
        query_vector = embed(query)
        if not any(query_vector):
            return []
        hits: list[ChunkHit] = []
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM chunks").fetchall()
        for row in rows:
            score = cosine(query_vector, json.loads(row["vector"]))
            if score < min_score:
                continue
            hits.append(
                ChunkHit(row["chunk_id"], row["doc_id"], row["title"], row["text"], score)
            )
        hits.sort(key=lambda hit: (-hit.score, hit.chunk_id))
        return hits[:top_k]
