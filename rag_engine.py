# ============================================================
# rag_engine.py — PRODUCTION-READY RAG ENGINE (WITH CHUNKING)
# ============================================================
# Features:
# - Load PDF & TXT documents
# - Chunk documents with overlap
# - Create embeddings using Sentence-Transformers
# - Store vectors in FAISS
# - Retrieve top-k relevant chunks
#
# This file is MODEL-AGNOSTIC
# Works with: Groq / Ollama / OpenAI
#
# Install:
#   pip install sentence-transformers faiss-cpu pypdf
# ============================================================

import os
from typing import List

import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader


class RAGEngine:
    def __init__(
        self,
        data_dir: str = "data",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 400,
        chunk_overlap: int = 50
    ):
        self.data_dir = data_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.embedder = SentenceTransformer(embedding_model)

        self.documents: List[str] = []
        self.embeddings = None
        self.index = None

        self._load_and_index_documents()

    # --------------------------------------------------------
    # TEXT CHUNKING
    # --------------------------------------------------------
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping word chunks.
        """
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk = words[start:end]
            chunks.append(" ".join(chunk))
            start += self.chunk_size - self.chunk_overlap

        return chunks

    # --------------------------------------------------------
    # LOAD DOCUMENTS (PDF / TXT)
    # --------------------------------------------------------
    def _load_documents(self) -> List[str]:
        texts = []

        os.makedirs(self.data_dir, exist_ok=True)

        for file in os.listdir(self.data_dir):
            path = os.path.join(self.data_dir, file)

            # ---------- PDF FILES
            if file.lower().endswith(".pdf"):
                try:
                    reader = PdfReader(path)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            chunks = self._chunk_text(page_text)
                            texts.extend(chunks)
                except Exception as e:
                    print(f"[RAG] PDF error ({file}): {e}")

            # ---------- TXT FILES
            elif file.lower().endswith(".txt"):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                        chunks = self._chunk_text(text)
                        texts.extend(chunks)
                except Exception as e:
                    print(f"[RAG] TXT error ({file}): {e}")

        # Remove empty chunks
        texts = [t.strip() for t in texts if t and t.strip()]
        return texts

    # --------------------------------------------------------
    # BUILD FAISS INDEX
    # --------------------------------------------------------
    def _build_faiss_index(self):
        if not self.documents:
            return

        self.embeddings = self.embedder.encode(
            self.documents,
            show_progress_bar=True
        )

        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

    # --------------------------------------------------------
    # LOAD + INDEX (ON STARTUP)
    # --------------------------------------------------------
    def _load_and_index_documents(self):
        self.documents = self._load_documents()

        if self.documents:
            self._build_faiss_index()
            print(f"[RAG] Loaded {len(self.documents)} chunks")
        else:
            print("[RAG] No documents found")

    # --------------------------------------------------------
    # RETRIEVE CONTEXT
    # --------------------------------------------------------
    def retrieve(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve top-k most relevant chunks for a query.
        """
        if not self.documents or self.index is None:
            return ""

        query_embedding = self.embedder.encode([query])
        _, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])

        return "\n\n".join(results)

    # --------------------------------------------------------
    # RELOAD DOCUMENTS (OPTIONAL)
    # --------------------------------------------------------
    def reload(self):
        """
        Reload documents and rebuild FAISS index.
        Use when new files are added to data/
        """
        self.documents = []
        self.embeddings = None
        self.index = None
        self._load_and_index_documents()


# ============================================================
# QUICK TEST (OPTIONAL)
# ============================================================
if __name__ == "__main__":
    rag = RAGEngine(data_dir="data")
    print("Chunks loaded:", len(rag.documents))
    print("\nSample retrieval:\n")
    print(rag.retrieve("Explain KNN algorithm", top_k=2))
