# Demonstrates: Metadata-driven KB loading with dimension validation.
# KB files are self-describing — the embedding model and dimension live in
# the metadata file, not in config or environment variables.
# Dimension mismatch is caught at load time, not silently at query time.
# Part of RAGEngine in ask_ai.py. Not standalone.

def load_kb(self, kb_name: str, models_root: Path):
    """
    Loads a FAISS index and its embedding model from metadata alone.

    Design: metadata file is the single source of truth.
    No hardcoded model names, no config files, no environment variables.
    The KB declares what model built it — the loader respects that declaration.

    Validation order:
    1. Find latest versioned FAISS + metadata file pair
    2. Load metadata, extract embedding_model and embedding_dim
    3. Validate FAISS index dimension matches metadata declaration
    4. Load embedding model, validate its output dimension matches both
    5. Validate document count matches FAISS vector count

    Any mismatch raises RuntimeError immediately — no silent corruption.
    """
    faiss_file = self.find_latest_file(self.kb_path, "faiss_index", ".bin")
    meta_file = self.find_latest_file(self.kb_path, "meta_map", ".pkl")

    if not faiss_file or not meta_file:
        raise RuntimeError(f"KB '{kb_name}' missing FAISS or metadata files")

    self.index = faiss.read_index(str(faiss_file))

    with open(meta_file, "rb") as f:
        meta_blob = pickle.load(f)

    self.meta_file_path = meta_file

    embed_model_name = meta_blob.get("embedding_model")
    embed_dim = meta_blob.get("embedding_dim")

    if not embed_model_name or not embed_dim:
        raise RuntimeError(f"KB '{kb_name}' metadata missing embedding_model or embedding_dim")

    # Validate FAISS dimension matches metadata declaration
    if int(self.index.d) != embed_dim:
        raise RuntimeError(
            f"KB '{kb_name}' dimension mismatch: FAISS={self.index.d}D vs Metadata={embed_dim}D"
        )

    # Build per-document metadata list
    documents = meta_blob.get("documents", [])
    if not documents:
        raise RuntimeError(f"KB '{kb_name}' contains no documents")

    self.meta = [dict(metadata) | {"text": text} for text, metadata in documents]

    # Validate document count matches vector count
    if len(self.meta) != self.index.ntotal:
        raise RuntimeError(
            f"KB '{kb_name}' FAISS/meta size mismatch: "
            f"{self.index.ntotal} vectors vs {len(self.meta)} documents"
        )

    # Load embedding model and validate its output dimension
    model_path = models_root / embed_model_name
    if not model_path.exists():
        raise FileNotFoundError(f"Embedding model not found: {model_path}")

    self.embedder = SentenceTransformer(str(model_path))
    test_dim = self.embedder.encode(["test"], convert_to_numpy=True).shape[1]

    if test_dim != embed_dim:
        raise RuntimeError(
            f"Model '{embed_model_name}' produces {test_dim}D but KB declares {embed_dim}D"
        )

    self.reranker = LocalReranker(self.embedder)
    self.embedding_model_name = embed_model_name
    self.embedding_dim = embed_dim
