# Demonstrates: Model and dimension validation at query time.
# Catches model drift — querying an index with a different embedding model
# than it was built with produces silently wrong results (high scores for
# semantically unrelated documents). This validation makes the failure loud.
# Part of merge_vector.py /api/topk endpoint. Not standalone.

def topk_search_validation(meta_data: dict) -> tuple:
    """
    Validates that the loaded FAISS index matches the active embedding model.

    Two checks before any query is executed:

    Check 1 — Model name match:
        The metadata blob stores the embedding model name used at index
        build time. If it doesn't match EMBEDDING_MODEL_NAME, the query
        would produce embeddings in a different semantic space.
        Returns HTTP 409 (conflict) with expected vs. found values.

    Check 2 — Dimension match:
        Even if model names match, quantization or fine-tuning can change
        output dimension. FAISS will silently accept the wrong dimension
        on some index types, producing garbage distances.
        Returns HTTP 409 (conflict) with expected vs. found values.

    Both checks return actionable error messages — the caller knows exactly
    what model/dimension the index expects and what was provided.
    """
    if meta_data.get("embedding_model") != EMBEDDING_MODEL_NAME:
        return False, {
            "status": "error",
            "message": "Embedding model mismatch — index was built with a different model",
            "expected": EMBEDDING_MODEL_NAME,
            "found": meta_data.get("embedding_model")
        }, 409

    if meta_data.get("embedding_dim") != EMBEDDING_DIM:
        return False, {
            "status": "error",
            "message": "Embedding dimension mismatch — index geometry incompatible",
            "expected": EMBEDDING_DIM,
            "found": meta_data.get("embedding_dim")
        }, 409

    return True, None, None


# In the /api/topk endpoint:
#
#   valid, error_body, status_code = topk_search_validation(meta_data)
#   if not valid:
#       return jsonify(error_body), status_code
