# Demonstrates: Per-model semantic reranking with batch encoding.
# Cosine similarity over raw FAISS L2 distance — prevents topic mismatch
# (e.g. "Python snakes" ranking above "Python exception handling").
# Batched for efficiency: 3-5x faster than sequential encoding.
# Part of ask_ai.py. Not standalone.

class LocalReranker:
    """
    Semantic reranker using the KB's own embedding model.
    One reranker instance per embedding model — shared across KBs
    that use the same model to avoid redundant memory loading.
    """

    def __init__(self, embedder: SentenceTransformer):
        self.embedder = embedder
        self.batch_size = 32

    def predict(self, pairs: list) -> list:
        """
        Scores query-candidate pairs by cosine similarity.

        Batch encoding strategy:
        - Concatenate all queries + all candidates into one list
        - Encode in batches of 32 (3-5x faster than one-at-a-time)
        - Split result array back into query and candidate halves
        - Dot product of normalized vectors = cosine similarity

        Returns scores in [0, 1] — directly comparable across models
        because all embeddings are L2-normalized before scoring.
        """
        if not pairs:
            return []

        query_texts, candidate_texts = zip(*pairs)
        all_texts = list(query_texts) + list(candidate_texts)

        # Batch encode
        if len(all_texts) > self.batch_size:
            all_embs = []
            for i in range(0, len(all_texts), self.batch_size):
                batch = all_texts[i:i + self.batch_size]
                batch_embs = self.embedder.encode(
                    batch,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                all_embs.append(batch_embs)
            all_embs = np.vstack(all_embs)
        else:
            all_embs = self.embedder.encode(
                all_texts,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

        query_embs = all_embs[:len(query_texts)]
        candidate_embs = all_embs[len(query_texts):]

        # Dot product of normalized vectors = cosine similarity
        return [float(np.dot(q.flatten(), c.flatten()))
                for q, c in zip(query_embs, candidate_embs)]
