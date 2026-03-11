# Demonstrates: Importance-weighted cosine similarity for RAG retrieval.
# Blends semantic similarity (70%) with chunk importance score (30%) to surface
# well-documented, frequently-referenced code over obscure utilities.
# Part of RAGEngine in my_coder.py. Not standalone.

def query(self, text: str, k: int = 3) -> list:
    """
    Retrieves k most relevant chunks using weighted similarity.
    Score = 0.7 * cosine_similarity + 0.3 * importance_weight
    """
    if self.vectors is None or len(self.metadata) == 0:
        return []

    query_vec = self._get_embedding(text)
    if query_vec is None:
        return []

    # Cosine similarity across all indexed chunks
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-12)
    norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
    vecs_norm = self.vectors / np.where(norms == 0, 1e-12, norms)
    sims = np.dot(vecs_norm, query_norm)

    # Blend similarity with importance — prevents low-quality chunks from ranking high
    importance_weights = np.array([m.get("importance", 0.5) for m in self.metadata])
    weighted_sims = sims * (0.7 + 0.3 * importance_weights)

    top_k_indices = np.argsort(weighted_sims)[::-1][:k]

    results = []
    for idx in top_k_indices:
        if weighted_sims[idx] > RAG_SIMILARITY_THRESHOLD and idx < len(self.metadata):
            chunk = self.metadata[idx].copy()
            chunk["similarity"] = float(sims[idx])
            chunk["weighted_score"] = float(weighted_sims[idx])
            results.append(chunk)

    return results
