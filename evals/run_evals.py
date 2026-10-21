#!/usr/bin/env python3
"""黄金集门禁。低于阈值时退出码为 1。"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scorers import mean, score_citation, score_no_invented  # noqa: E402
from citation_rag.models import DocumentIn  # noqa: E402
from citation_rag.qa import ask, ingest  # noqa: E402
from citation_rag.store import Store  # noqa: E402

THRESHOLDS = {
    "citation_present_when_expected": 1.0,
    "no_invented_citations": 1.0,
}

CORPUS = Path(__file__).parent / "golden" / "corpus.json"
QUESTIONS = Path(__file__).parent / "golden" / "questions.jsonl"
REPORT_PATH = Path(__file__).parent / "last_report.json"


def main() -> int:
    documents = json.loads(CORPUS.read_text(encoding="utf-8"))
    questions = [
        json.loads(line)
        for line in QUESTIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    citation_scores: list[float | None] = []
    invented_scores: list[float | None] = []
    cases: list[dict] = []

    with tempfile.TemporaryDirectory() as tmp:
        store = Store(Path(tmp) / "rag.db")
        for document in documents:
            ingest(DocumentIn(**document), store)
        for item in questions:
            result = ask(item["question"], store)
            doc_ids = [citation.doc_id for citation in result.citations]
            citation_score = score_citation(doc_ids, item["expect_doc_prefix"])
            invented_score = score_no_invented(doc_ids, item["forbid_citations"])
            citation_scores.append(citation_score)
            invented_scores.append(invented_score)
            cases.append(
                {
                    "id": item["id"],
                    "abstained": result.abstained,
                    "doc_ids": doc_ids,
                    "citation_score": citation_score,
                    "invented_score": invented_score,
                }
            )

    metrics = {
        "citation_present_when_expected": mean(citation_scores),
        "no_invented_citations": mean(invented_scores),
    }
    report = {"metrics": metrics, "thresholds": THRESHOLDS, "cases": cases}
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    failed = [name for name, threshold in THRESHOLDS.items() if metrics[name] < threshold]
    if failed:
        print("FAIL " + ",".join(failed))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
