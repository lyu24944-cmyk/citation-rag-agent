"""确定性哈希向量。不下载模型，测试和演示都不需要 API Key。"""

from __future__ import annotations

import hashlib
import math

from citation_rag.text import tokenize

DIM = 256


def embed(text: str) -> list[float]:
    """把文本映到单位长度的稀疏向量。空文本得到零向量。"""
    vector = [0.0] * DIM
    tokens = tokenize(text)
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.md5(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "little") % DIM
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    """两边都已归一化时，点积就是余弦相似度。"""
    return sum(a * b for a, b in zip(left, right))
