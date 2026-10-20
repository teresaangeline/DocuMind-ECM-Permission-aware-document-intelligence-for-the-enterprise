"""ChromaDB wrapper. Access level is stored as chunk metadata and enforced in the query."""

import chromadb

from app.config import settings

_collection = None


def _col():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(settings.data_dir / "chroma"))
        _collection = client.get_or_create_collection("documents")
    return _collection


def add_chunks(doc_id: str, filename: str, access_level: str, chunks) -> None:
    if not chunks:
        return
    _col().add(
        ids=[f"{doc_id}-{c.index}" for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[
            {"doc_id": doc_id, "filename": filename, "page": c.page,
             "access_level": access_level}
            for c in chunks
        ],
    )


def search(question: str, levels: list[str], k: int) -> list[dict]:
    res = _col().query(
        query_texts=[question],
        n_results=k,
        where={"access_level": {"$in": levels}},  # security enforced at retrieval time
    )
    return [
        {"text": t, **m, "distance": d}
        for t, m, d in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0], strict=True
        )
    ]
