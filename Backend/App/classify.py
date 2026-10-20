"""Classification + metadata extraction (the Documentum 'object type + attributes' idea)."""

import json
import re

from app import llm

DOC_TYPES = ["invoice", "contract", "resume", "policy", "report", "letter", "other"]

SYSTEM = (
    "You are a document-capture engine. Classify the document and extract key fields. "
    f"doc_type must be one of {DOC_TYPES}. "
    'Reply with ONLY JSON: {"doc_type": str, "summary": str, "fields": {str: str}}. '
    "For invoices include invoice_number, vendor, date, total. For contracts include "
    "parties, effective_date, term. Omit fields you cannot find; never invent values."
)


def parse_json(raw: str) -> dict:
    """Tolerant JSON parse: strips code fences and surrounding prose."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("Model did not return JSON")
    data = json.loads(match.group(0))
    doc_type = data.get("doc_type", "other")
    return {
        "doc_type": doc_type if doc_type in DOC_TYPES else "other",
        "summary": str(data.get("summary", "")),
        "fields": data.get("fields") if isinstance(data.get("fields"), dict) else {},
    }


def classify_and_extract(text: str) -> dict:
    try:
        return parse_json(llm.complete(SYSTEM, text[:6000], max_tokens=600))
    except Exception:  # classification must never block ingestion
        return {"doc_type": "other", "summary": "", "fields": {}}
