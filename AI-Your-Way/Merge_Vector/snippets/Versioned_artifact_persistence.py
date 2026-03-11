# Demonstrates: Versioned artifact persistence with full metadata blob.
# Each vectorization run produces a timestamped FAISS index + metadata pair.
# The metadata blob is the contract between Phase 2 and Phase 3 — it carries
# everything ask_ai.py needs to validate and load the index correctly.
# Part of merge_vector.py /api/vectorize endpoint. Not standalone.

def get_versioned_filename(file_type: str, model_name: str, ext: str) -> str:
    """
    Generates a timestamped filename so every vectorization run is preserved.

    Format: {file_type}_{model_name}_{YYYYMMDD_HHMMSS}.{ext}
    Example: faiss_index_mpnet_20250115_143022.bin

    Why timestamp-versioned instead of overwriting:
    - Multiple JSONL files can be vectorized without colliding
    - Rollback to a prior index is a config change, not a rebuild
    - ask_ai.py's /api/kb/browse endpoint discovers all versions automatically
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(VAULT_DIR / f"{file_type}_{model_name}_{timestamp}.{ext}")


# Metadata blob structure — the Phase 2 → Phase 3 contract.
# ask_ai.py reads embedding_model and embedding_dim at load time
# and validates them against the active embedding model.
# No fields are optional: missing any of these causes a load-time error,
# not a silent query-time degradation.

def persist_index_artifacts(index, filtered_documents, outliers_idx):
    faiss_index_file = get_versioned_filename("faiss_index", "mpnet", "bin")
    meta_map_file    = get_versioned_filename("meta_map",    "mpnet", "pkl")

    faiss.write_index(index, faiss_index_file)

    with open(meta_map_file, "wb") as f:
        pickle.dump({
            "embedding_model": EMBEDDING_MODEL_NAME,   # validated by ask_ai at load time
            "embedding_dim":   EMBEDDING_DIM,          # validated by ask_ai at load time
            "created_at":      datetime.utcnow().isoformat(),
            "total_chunks":    len(filtered_documents),
            "outliers_removed": len(outliers_idx),
            "documents":       filtered_documents      # (text, metadata) pairs — full Phase 1 provenance
        }, f)

    return faiss_index_file, meta_map_file
