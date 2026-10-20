from app import llm, vectorstore
from app.config import settings
from app.security import allowed_levels

SYSTEM = (
    "Answer the question using ONLY the numbered context passages. "
    "Cite sources inline like [1], [2]. If the context does not contain the answer, "
    "say you could not find it in the documents you have access to."
)


def build_prompt(question: str, passages: list[dict]) -> str:
    ctx = "\n\n".join(
        f"[{i}] ({p['filename']}, p.{p['page']}) {p['text']}"
        for i, p in enumerate(passages, start=1)
    )
    return f"Context:\n{ctx}\n\nQuestion: {question}"


def answer(question: str, role: str) -> dict:
    levels = allowed_levels(role)
    passages = vectorstore.search(question, levels, settings.top_k)
    if not passages:
        return {
            "answer": "No accessible documents match your question.",
            "sources": [],
        }
    text = llm.complete(SYSTEM, build_prompt(question, passages))
    sources = [
        {"ref": i, "filename": p["filename"], "page": p["page"],
         "access_level": p["access_level"], "snippet": p["text"][:200]}
        for i, p in enumerate(passages, start=1)
    ]
    return {"answer": text, "sources": sources}
