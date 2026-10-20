import os

import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="DocuMind ECM", page_icon="📄", layout="wide")
st.title("📄 DocuMind ECM")
st.caption("Classify, extract and query enterprise documents, with role-based security.")

role = st.sidebar.selectbox("Acting as role", ["employee", "manager", "admin"], index=0)
st.sidebar.info("employee: public · manager: + internal · admin: + confidential")

tab_upload, tab_docs, tab_ask = st.tabs(["Upload", "Documents", "Ask"])

with tab_upload:
    f = st.file_uploader("PDF / TXT / MD", type=["pdf", "txt", "md"])
    level = st.selectbox("Access level", ["public", "internal", "confidential"], index=1)
    if f and st.button("Ingest"):
        with st.spinner("Extracting, classifying, indexing..."):
            r = requests.post(
                f"{API}/documents",
                files={"file": (f.name, f.getvalue())},
                data={"access_level": level},
                timeout=120,
            )
        if r.ok:
            st.success(f"Detected type: {r.json()['doc_type']}")
            st.json(r.json())
        else:
            st.error(r.json().get("detail", r.text))

with tab_docs:
    r = requests.get(f"{API}/documents", params={"role": role}, timeout=30)
    docs = r.json() if r.ok else []
    st.write(f"{len(docs)} document(s) visible to **{role}**")
    for d in docs:
        with st.expander(f"{d['filename']} · {d['doc_type']} · {d['access_level']}"):
            st.write(d["summary"])
            st.json(d["fields"])

with tab_ask:
    q = st.text_input("Ask a question about your documents")
    if q and st.button("Ask"):
        r = requests.post(f"{API}/ask", json={"question": q, "role": role}, timeout=120)
        if r.ok:
            out = r.json()
            st.markdown(out["answer"])
            for s in out["sources"]:
                st.caption(f"[{s['ref']}] {s['filename']} p.{s['page']} ({s['access_level']})")
        else:
            st.error(r.json().get("detail", r.text))
