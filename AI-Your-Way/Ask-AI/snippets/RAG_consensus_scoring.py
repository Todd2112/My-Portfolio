# Demonstrates: RAG consensus scoring using 60th percentile similarity.
# Measures agreement between the final answer and retrieved snippets.
# 60th percentile chosen deliberately over mean/median — see rationale below.
# Part of RAGEngine in ask_ai.py. Not standalone.

def rag_consensus_signal(self, answer_emb: np.ndarray, snippet_embs: np.ndarray) -> float:
    """
    Scores how well the final answer agrees with the retrieved KB snippets.
    Used as one of five weighted signals in the confidence scoring system.

    Why 60th percentile instead of mean or median:
    - Mean: one low-quality outlier snippet tanks the entire score
    - Median: ignores the top-quality snippets entirely
    - 60th percentile: captures overall agreement while tolerating a few weak matches

    Returns consensus score [0, 1].
    """
    if snippet_embs is None or len(snippet_embs) == 0:
        return 0.0

    if answer_emb.ndim > 1 and answer_emb.shape[0] == 1:
        answer_emb = answer_emb.flatten()

    sims = np.dot(snippet_embs, answer_emb).flatten()

    if sims.size == 0:
        return 0.0

    return float(np.percentile(sims, 60))
