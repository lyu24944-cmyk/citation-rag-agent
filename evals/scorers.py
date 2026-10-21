"""确定性打分。无关问题必须零引用。"""

from __future__ import annotations


def score_citation(doc_ids: list[str], prefix: str | None) -> float | None:
    """期望命中某文档时，引用里是否出现该前缀。"""
    if not prefix:
        return None
    if not doc_ids:
        return 0.0
    matched = all(doc_id.startswith(prefix) for doc_id in doc_ids)
    return 1.0 if matched else 0.0


def score_no_invented(doc_ids: list[str], forbid: bool) -> float | None:
    """禁止编造时，引用列表必须为空。"""
    if not forbid:
        return None
    return 1.0 if not doc_ids else 0.0


def mean(values: list[float | None]) -> float:
    kept = [value for value in values if value is not None]
    if not kept:
        return 1.0
    return sum(kept) / len(kept)
