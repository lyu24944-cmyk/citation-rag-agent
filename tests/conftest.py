import pytest

from citation_rag.store import Store


@pytest.fixture
def store(tmp_path) -> Store:
    return Store(tmp_path / "rag.db")
