"""HTTP API：入库与提问。"""

from fastapi import FastAPI

from citation_rag import __version__
from citation_rag.config import resolve_db_path, settings
from citation_rag.models import AskRequest, AskResult, DocumentIn, IngestResult
from citation_rag.qa import ask, ingest
from citation_rag.store import Store


def create_app(store: Store | None = None) -> FastAPI:
    """传入 store 时测试用临时库，否则用配置路径。"""
    app = FastAPI(title=settings.app_name, version=__version__)
    app.state.store = store if store is not None else Store(resolve_db_path())

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "version": __version__, "chunks": app.state.store.count()}

    @app.post("/documents", response_model=IngestResult)
    def add_document(document: DocumentIn) -> IngestResult:
        return ingest(document, app.state.store)

    @app.post("/ask", response_model=AskResult)
    def ask_question(request: AskRequest) -> AskResult:
        return ask(request.question, app.state.store, top_k=request.top_k)

    return app


app = create_app()


def run() -> None:
    """入口：启动 uvicorn。"""
    import uvicorn

    uvicorn.run("citation_rag.api.main:app", host="127.0.0.1", port=8001, reload=False)


if __name__ == "__main__":
    run()
