from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app import classify, db, ingest, rag, vectorstore
from app.config import settings
from app.security import allowed_levels

app = FastAPI(title="DocuMind ECM", version="0.1.0")

AccessLevel = Literal["public", "internal", "confidential"]
Role = Literal["employee", "manager", "admin"]


class AskRequest(BaseModel):
    question: str
    role: Role = "employee"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    access_level: AccessLevel = Form("internal"),
):
    data = await file.read()
    try:
        pages = ingest.extract_pages(file.filename or "upload", data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    chunks = ingest.chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    meta = classify.classify_and_extract("\n".join(pages))
    doc = db.insert_document(
        file.filename, access_level, meta["doc_type"], meta["summary"],
        meta["fields"], len(chunks),
    )
    vectorstore.add_chunks(doc["id"], file.filename, access_level, chunks)
    return doc


@app.get("/documents")
def list_documents(role: Role = "admin"):
    return db.list_documents(allowed_levels(role))


@app.post("/ask")
def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="Question is empty")
    try:
        return rag.answer(req.question, req.role)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
