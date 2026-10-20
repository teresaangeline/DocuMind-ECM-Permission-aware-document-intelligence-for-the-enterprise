"""Capture step (Captiva-style): extract text per page, then chunk it."""

import io
from dataclasses import dataclass

from pypdf import PdfReader


@dataclass
class Chunk:
    text: str
    page: int
    index: int


def extract_pages(filename: str, data: bytes) -> list[str]:
    """Return text per page. PDFs via pypdf; .txt/.md decoded directly."""
    name = filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        pages = [(p.extract_text() or "").strip() for p in reader.pages]
        if not any(pages):
            # Scanned PDF with no text layer. OCR (e.g. Tesseract) plugs in here.
            raise ValueError(
                "No extractable text found (scanned PDF?). OCR is on the roadmap."
            )
        return pages
    if name.endswith((".txt", ".md")):
        return [data.decode("utf-8", errors="ignore")]
    raise ValueError("Unsupported file type. Upload a PDF, TXT or MD file.")


def chunk_pages(pages: list[str], size: int = 800, overlap: int = 100) -> list[Chunk]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks: list[Chunk] = []
    for page_no, text in enumerate(pages, start=1):
        text = " ".join(text.split())
        start = 0
        while start < len(text):
            piece = text[start : start + size]
            if piece.strip():
                chunks.append(Chunk(piece, page_no, len(chunks)))
            start += size - overlap
    return chunks
