# utils.py
"""
Helpers for PDF extraction, chunking, embedding and retrieval (Chroma).
"""


from pypdf import PdfReader
import os, re
import chromadb
from sentence_transformers import SentenceTransformer

# Config
EMBED_MODEL = "all-MiniLM-L6-v2"
CHROMA_DIR = "db"
COLLECTION_NAME = "math_books"

# -----------------------
# PDF / chunk utilities
# -----------------------
def extract_text_from_pdf(path: str) -> str:
    """Return concatenated text of all pages in the PDF file at `path`."""
    reader = PdfReader(path)
    pages = []
    for p in reader.pages:
        txt = p.extract_text()
        if txt:
            pages.append(txt)
    return "\n".join(pages)

def split_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Split `text` into overlapping character chunks."""
    if not text:
        return []
    text = re.sub(r'\s+', ' ', text).strip()
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + chunk_size)
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return chunks

def load_pdfs_from_folder(folder: str) -> list:
    """
    Read every .pdf in `folder` and return list of dicts:
    { 'id': '<filename>___<chunk_index>', 'text': '<chunk text>', 'source': '<filename>', 'chunk': i }
    """
    results = []
    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(folder, fname)
        text = extract_text_from_pdf(path)
        chunks = split_into_chunks(text)
        for i, c in enumerate(chunks):
            results.append({
                "id": f"{fname}___{i}",
                "text": c,
                "source": fname,
                "chunk": i
            })
    return results

# -----------------------
# Embeddings & Chroma
# -----------------------
_embedder = None
def get_embedder(model_name: str = EMBED_MODEL):
    """Return a (cached) SentenceTransformer embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(model_name)
    return _embedder

def get_chroma_collection(persist_dir: str = CHROMA_DIR, collection_name: str = COLLECTION_NAME):
    """
    Return only the Chroma collection object.
    Works with chromadb.PersistentClient or chromadb.Client depending on your package version.
    """
    try:
        # Try PersistentClient first
        client = chromadb.PersistentClient(path=persist_dir)
    except Exception:
        try:
            from chromadb.config import Settings
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir
            ))
        except Exception:
            # Last fallback
            client = chromadb.Client()

    # Get or create the collection
    try:
        coll = client.get_collection(collection_name)
    except Exception:
        coll = client.get_or_create_collection(name=collection_name)

    return coll   # ✅ Return only collection


def query_collection(question: str, k: int = 5) -> list:
    """
    Return up to k most relevant chunks for `question`.
    Each result is a dict: {'document': <clean text>, 'metadata': <meta dict>, 'distance': <float or None>}
    """
    coll = get_chroma_collection()   # ✅ just returns collection
    embedder = get_embedder()
    q_emb = embedder.encode([question], convert_to_numpy=True).tolist()

    try:
        results = coll.query(
            query_embeddings=q_emb,
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        docs = results.get("documents", [])[0]
        metas = results.get("metadatas", [])[0]
        dists = results.get("distances", [])[0] if "distances" in results else [None] * len(docs)
    except Exception as e:
        print("Query failed:", e)
        return []

    out = []
    for doc, meta, dist in zip(docs, metas, dists):
        # 🧹 Clean the text
        clean_doc = " ".join(doc.split())   # removes newlines & extra spaces
        out.append({"document": clean_doc, "metadata": meta, "distance": dist})
    return out



def build_prompt(question: str, docs: list) -> str:
    """
    Create a prompt that includes retrieved context plus the user's question.
    The LLM should use ONLY the provided context when answering.
    """
    context = ""
    for d in docs:
        meta = d.get("metadata", {}) or {}
        src = meta.get("source", "unknown")
        chunk_idx = meta.get("chunk", "?")
        context += f"Source: {src}, chunk: {chunk_idx}\n{d.get('document','')}\n\n"
    prompt = f"""
You are a patient expert math tutor. Use ONLY the CONTEXT below (extracted from the student's course books) to answer the QUESTION.
Show clear step-by-step calculations and a final boxed answer. Use LaTeX for equations where helpful.

CONTEXT:
{context}

QUESTION:
{question}

Answer:
"""
    return prompt.strip()
 
