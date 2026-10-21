"""切块与分词。中文按二字词，避免单字把无关句子连在一起。"""

from __future__ import annotations

import re

_LATIN = re.compile(r"[a-z0-9]+")
_CJK = re.compile(r"[\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    """拉丁词整词保留；中文取相邻两字。只有一个汉字时才保留单字。"""
    lowered = (text or "").lower()
    tokens = _LATIN.findall(lowered)
    chars = _CJK.findall(lowered)
    if len(chars) >= 2:
        tokens.extend(a + b for a, b in zip(chars, chars[1:]))
    elif len(chars) == 1:
        tokens.append(chars[0])
    return tokens


def chunk_text(text: str, size: int = 180, overlap: int = 40) -> list[str]:
    """先按空行分段，超长段再按窗口切开。"""
    raw = (text or "").strip()
    if not raw:
        return []
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", raw) if part.strip()]
    pieces: list[str] = []
    step = max(1, size - overlap)
    for para in paragraphs:
        if len(para) <= size:
            pieces.append(para)
            continue
        start = 0
        while start < len(para):
            piece = para[start : start + size].strip()
            if piece:
                pieces.append(piece)
            if start + size >= len(para):
                break
            start += step
    return pieces
