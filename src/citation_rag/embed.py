"""多语言句子嵌入。模型缓存在仓库 .data/models，下载一次后可离线加载。"""

from __future__ import annotations

import math
from pathlib import Path

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_MODEL = None


def model_cache_dir() -> Path:
    """权重不入库。"""
    path = Path(__file__).resolve().parents[2] / ".data" / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_model():
    global _MODEL
    if _MODEL is None:
        from fastembed import TextEmbedding

        _MODEL = TextEmbedding(MODEL_NAME, cache_dir=str(model_cache_dir()))
    return _MODEL


def embed(text: str) -> list[float]:
    """返回单位向量。空文本得到空列表，调用方应视为没有检索结果。"""
    raw = (text or "").strip()
    if not raw:
        return []
    values = [float(item) for item in next(_get_model().embed([raw]))]
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return []
    return [value / norm for value in values]


def cosine(left: list[float], right: list[float]) -> float:
    """两边都已归一化时，点积就是余弦相似度。"""
    return sum(a * b for a, b in zip(left, right))
