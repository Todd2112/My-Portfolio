# Demonstrates: 8-stage multi-KB query pipeline with cross-model score fusion.
# Each stage has a clear contract — retrieval, reranking, fusion, extraction,
# augmentation, validation, confidence scoring, web fallback.
# Part of ask_ai.py. Not standalone.

def process_query_pipeline(query_text, active_kbs, rag_engines, rerankers):
    """
    Full query pipeline. Eight stages, three LLMs, one structured response.

    Stage 1 — Multi-KB retrieval:
        Query each active KB with its own embedding model via FAISS.
        Each result annotated with source_kb and kb_model for downstream routing.

    Stage 2 — Per-model reranking:
        Group results by embedding model. Rerank each group with its own
        LocalReranker instance. Prevents cross-model score contamination.

    Stage 3 — Cross-KB score fusion:
        Merge all reranked groups, sort by rerank score descending.
        Rerank scores are comparable across models (normalized cosine [0,1]).

    Stage 4 — Answer extraction:
        Pull text from best-scoring entry. Clean wiki artifacts and footnotes.

    Stage 5 — LLM augmentation (optional):
        Reasoning agent (8B) refines answer for clarity.
        Gated by augmentation_validation — rejected if keyword overlap < 30%
        or embedding similarity < 70%.

    Stage 6 — Confidence scoring:
        Five weighted signals: outcome type, user feedback, RAG consensus,
        rerank score, statistical baseline. Normalized [-1,1] → [0,1].

    Stage 7 — Web fallback:
        DuckDuckGo search activates only if KB produced no answer.
        5-second timeout. Snippet truncated at sentence boundary.

    Stage 8 — Structured response:
        Returns answer, all scoring signals, source metadata, session length.
    """
    all_retrieved = []

    # Stage 1: Multi-KB retrieval
    for kb_key in active_kbs:
        if kb_key not in rag_engines:
            continue
        engine = rag_engines[kb_key]
        query_emb = engine.encode_query(query_text)
        kb_results = engine.topk_retrieve(query_emb, TOP_K_RETRIEVE)
        for r in kb_results:
            r["source_kb"] = kb_key
            r["kb_model"] = engine.embedding_model_name
        all_retrieved.extend(kb_results)

    # Stage 2: Per-model reranking (grouped by model)
    reranked, scores = [], []
    by_model = {}
    for r in all_retrieved:
        by_model.setdefault(r.get("kb_model", "unknown"), []).append(r)

    for model, results in by_model.items():
        if model in rerankers:
            model_reranked, model_scores = rerank_results(query_text, results, rerankers[model])
            reranked.extend(model_reranked)
            scores.extend(model_scores)

    # Stage 3: Cross-KB score fusion
    if reranked:
        combined = sorted(zip(reranked, scores), key=lambda x: x[1], reverse=True)
        reranked, scores = map(list, zip(*combined))

    # Stage 4: Answer extraction
    best_entry = reranked[0] if reranked else None
    best_rerank_score = scores[0] if scores else 0.0
    source_kb = best_entry.get("source_kb") if best_entry else None
    best_answer_raw = extract_text(best_entry).strip() if best_entry else None

    answer, kb_answer, source_type, augmented = "", None, "NONE", False

    # Stage 5: Augmentation with validation gate
    if best_answer_raw and len(best_answer_raw) > 20:
        kb_answer = clean_kb_text(best_answer_raw)
        answer = format_answer_human_readable(kb_answer)
        source_type = "KB_DIRECT"

        if ENABLE_LLM_AUGMENTATION and best_rerank_score >= AUGMENTATION_MIN_RERANK:
            answer, augmented = augment_answer_with_llm(
                kb_answer, query_text, reranked, source_kb, rag_engines
            )
            if augmented:
                source_type = "KB_AUGMENTED"

    # Stage 6: Web fallback
    if not answer or answer in ["LLM_FAIL", "LLM_UNAVAILABLE"]:
        web_result = online_fallback(query_text, use_async=True)
        if web_result.startswith("WEB_SUCCESS"):
            answer = web_result.split(": ", 1)[-1]
            source_type = "WEB"
        else:
            answer = "I couldn't find an answer in my knowledge base or online."
            source_type = "FAIL"

    # Stage 7: Confidence scoring
    rag_score = 0.0
    if reranked and source_kb in rag_engines:
        try:
            engine = rag_engines[source_kb]
            snippet_embs = np.array([
                r["embedding"] for r in reranked
                if isinstance(r.get("embedding"), np.ndarray)
            ])
            if snippet_embs.size > 0:
                answer_emb = engine.embedder.encode(
                    [answer], convert_to_numpy=True, normalize_embeddings=True
                )
                rag_score = engine.rag_consensus_signal(answer_emb, snippet_embs)
        except Exception:
            pass

    confidence = compute_confidence({
        "outcome": OUTCOME_MAP.get(source_type, 0.0),
        "user": 0.0,
        "rag": rag_score,
        "rerank": best_rerank_score,
        "stat": 0.5
    })

    # Stage 8: Structured response
    return {
        "status": "success",
        "query": query_text,
        "answer": answer,
        "kb_answer": kb_answer,
        "source_type": source_type,
        "source_kb": source_kb,
        "confidence": confidence,
        "rerank_score": best_rerank_score,
        "rag_score": rag_score,
        "retrieved_count": len(all_retrieved),
        "augmented": augmented
    }
