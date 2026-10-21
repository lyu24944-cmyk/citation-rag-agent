"""运行时配置。测试不需要 API Key。"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """可用环境变量覆盖。数据库默认在仓库内的 .data。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "citation-rag-agent"
    db_path: str | None = None
    top_k: int = 3
    min_score: float = 0.15
    chunk_size: int = 180
    chunk_overlap: int = 40


settings = Settings()


def resolve_db_path() -> Path:
    """默认库文件放在仓库 .data，而不是上一级目录。"""
    if settings.db_path:
        path = Path(settings.db_path)
    else:
        path = Path(__file__).resolve().parents[2] / ".data" / "rag.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
