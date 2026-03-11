# Demonstrates: Triple-LLM orchestration — three models routed by task complexity.
# Each model handles only what it's sized for. The 1B classifier never sees
# reasoning tasks. The 8B reasoner is only invoked when multi-hop link analysis
# is actually needed. Part of ai-train.py. Not standalone.

# Model assignments (set at initialization):
#   llm_classifier = LLMManager("llama3.2:1b-instruct-q4_K_M")  — fast, deterministic
#   llm_parser     = LLMManager("llama3.2:3b-instruct-q8_0")    — summaries, entities
#   llm_reasoner   = LLMManager("llama3:8b-instruct-q5_K_M")    — link analysis, reasoning

def process_document(text: str, source: str, goal: str = "") -> dict:
    """
    Core ingestion pipeline. Six stages, three LLMs, one JSONL output.

    Stage 1 — Link reasoning     [llm_reasoner, 8B]  invoked BEFORE text cleaning
                                                       so raw HTML link context is preserved
    Stage 2 — Normalization      [no LLM]             HTML sanitization, whitespace cleanup
    Stage 3 — Classification     [llm_classifier, 1B] temperature 0.0, returns one label
    Stage 4 — Chunking           [no LLM]             sentence-boundary splits + goal filtering
    Stage 5 — Persistence        [llm_parser, 3B]     entity extraction on first chunk only
    Stage 6 — Summary            [llm_parser, 3B]     1-2 sentence topic summary
    """

    # Stage 1: Link reasoning before cleaning (8B — needs raw HTML context)
    recommended_actions = []
    if goal and source.startswith("http"):
        recommended_actions = analyze_relevant_links(text, source, goal, llm_reasoner)

    # Stage 2: Normalize
    clean_text = normalize_input(text, source)
    if not clean_text:
        return {"status": "error", "message": "No readable text found"}

    # Stage 3: Classify (1B — temperature 0.0, 8-token output, single label)
    sample = clean_text[:3000]
    sample = re.sub(r'\b\d{3,}\b', '', sample)   # strip numeric tables before classification
    sample = re.sub(r'\|+', ' ', sample)
    sample = re.sub(r'\s+', ' ', sample).strip()

    category = classify_document(sample, llm_classifier)

    # Stage 4: Chunk + goal filter
    chunks = chunk_text(clean_text)
    if goal:
        chunks = filter_chunks_by_goal(chunks, goal)

    if not chunks:
        return {"status": "error", "message": "No chunks created after filtering"}

    # Stage 5: Persist with relationships (3B for entity extraction, first chunk only)
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    total_chunks = len(chunks)
    total_tokens = 0
    persisted = 0

    for i, chunk in enumerate(chunks):
        tokens = estimate_tokens(chunk)
        total_tokens += tokens
        if persist_chunk(
            f"{doc_id}_chunk_{i}", doc_id, source, category,
            chunk, i, total_chunks, llm_parser
        ):
            persisted += 1

    # Stage 6: Summary (3B — PDF-aware prompt, 128-token output)
    summary = generate_summary_statement(
        doc_id, source, category, persisted, total_tokens, llm_parser
    )

    return {
        "status": "success",
        "doc_id": doc_id,
        "category": category,
        "chunks_created": persisted,
        "total_tokens": total_tokens,
        "summary": summary,
        "recommended_links": recommended_actions
    }
