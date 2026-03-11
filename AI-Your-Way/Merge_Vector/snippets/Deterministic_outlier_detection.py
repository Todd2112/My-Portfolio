# Demonstrates: Deterministic outlier detection before FAISS index construction.
# All embeddings computed FIRST, then filtered — prevents order-dependent
# results where incremental filtering would produce different indexes
# from the same input depending on processing sequence.
# Part of merge_vector.py. Not standalone.

def build_faiss_index(documents: list, outlier_thresh: float = 3.0, exclude_outliers: bool = True):
    """
    Builds a FAISS IndexFlatL2 from document embeddings with statistical outlier removal.

    Why deterministic ordering matters:
    Outlier detection using running statistics changes which points are flagged
    depending on the order documents are processed. This implementation computes
    ALL embeddings first, then derives a stable mean/std from the complete set.
    Same input always produces the same index — reproducible and auditable.

    Outlier threshold:
    A document is flagged if its distance from the centroid exceeds
    (outlier_thresh × std_norm). Default 3.0 follows the 3-sigma rule —
    retains 99.7% of a normal distribution, removes genuine outliers.
    """
    model = get_model()
    texts = [text for text, _ in documents]

    # Step 1: Compute ALL embeddings before any filtering (deterministic)
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Step 2: Stable mean/std from the complete embedding set
    mean = np.mean(embeddings, axis=0)
    std = np.std(embeddings, axis=0)
    std_norm = np.linalg.norm(std)

    # Step 3: Flag outliers by L2 distance from centroid
    outliers_idx = []
    if exclude_outliers and std_norm > 0:
        for idx, vec in enumerate(embeddings):
            distance = np.linalg.norm(vec - mean)
            if distance > outlier_thresh * std_norm:
                outliers_idx.append(idx)

    # Step 4: Filter both embeddings and documents in sync
    if outliers_idx and exclude_outliers:
        embeddings = np.delete(embeddings, outliers_idx, axis=0)
        documents = [doc for idx, doc in enumerate(documents) if idx not in outliers_idx]

    # Step 5: Build FAISS flat L2 index (exact search, best for <100k vectors)
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(embeddings)

    return index, documents, outliers_idx
