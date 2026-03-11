# Demonstrates: Semantic validation gate for LLM answer augmentation.
# LLMs improve clarity but also hallucinate. This gate rejects augmented answers
# that drift from the original KB content using two independent checks.
# Part of ask_ai.py answer pipeline. Not standalone.

def augment_answer_with_llm(kb_answer, query, reranked, source_kb, rag_engines):
    """
    Refines a KB answer using the reasoning LLM, then validates the result.

    Two-check validation before accepting augmentation:

    Check 1 — Keyword overlap (30% minimum):
        Extracts 4+ char content words from both the original KB answer and the
        augmented output. If fewer than 30% of the original keywords appear in
        the augmented answer, the topic has drifted — reject.

    Check 2 — Embedding similarity (70% minimum):
        Encodes both answers with the KB's own embedding model and computes
        cosine similarity. Below 0.70 means semantic divergence — reject.

    If either check fails, returns the original KB answer unchanged.
    Augmentation is never silently accepted.
    """
    if not REASONING_AGENT:
        return kb_answer, False

    context = synthesize_multi_snippet_answer(query, reranked, top_n=3)
    context = (context or kb_answer)[:MAX_CONTEXT_LENGTH]

    messages = [
        {
            "role": "system",
            "content": "You refine and clarify answers without adding new information."
        },
        {
            "role": "user",
            "content": (
                "CORE ANSWER (do not contradict):\n"
                f"{kb_answer}\n\n"
                "SUPPORTING CONTEXT:\n"
                f"{context}\n\n"
                "Improve clarity only. Remove footnotes and formatting artifacts.\n\n"
                f"Question: {query}"
            )
        }
    ]

    augmented = REASONING_AGENT.chat(messages)

    if not augmented or augmented in ["LLM_FAIL", "LLM_UNAVAILABLE"]:
        return kb_answer, False

    # Check 1: Keyword overlap
    core_kw = get_content_keywords(kb_answer)
    aug_kw = get_content_keywords(augmented)

    if not core_kw:
        return kb_answer, False

    overlap = len(core_kw & aug_kw) / len(core_kw)

    # Check 2: Embedding similarity
    semantic = 0.0
    if source_kb in rag_engines:
        try:
            embedder = rag_engines[source_kb].embedder
            kb_emb = embedder.encode([kb_answer], normalize_embeddings=True)[0]
            aug_emb = embedder.encode([augmented], normalize_embeddings=True)[0]
            semantic = cosine_similarity(kb_emb, aug_emb)
        except Exception:
            pass

    # Accept only if both thresholds pass
    if overlap >= 0.30 and semantic >= AUGMENTATION_SEMANTIC_THRESHOLD:
        return augmented, True
    else:
        return kb_answer, False  # original answer preserved
