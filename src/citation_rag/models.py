from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    """入库文档。"""

    doc_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    body: str


class IngestResult(BaseModel):
    """入库结果。"""

    doc_id: str
    chunk_count: int


class Citation(BaseModel):
    """回答所依据的一个文本块。"""

    chunk_id: str
    doc_id: str
    title: str
    excerpt: str
    score: float


class AskRequest(BaseModel):
    """一次提问。"""

    question: str
    top_k: int = Field(default=3, ge=1, le=10)


class AskResult(BaseModel):
    """回答。abstained 为真时 citations 必须为空。"""

    question: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    abstained: bool = False
