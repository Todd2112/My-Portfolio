# Demonstrates: Append-only JSONL persistence with chunk relationship tracking.
# Every chunk stores prev/next chunk IDs so retrieval systems can reconstruct
# document flow — essential for context continuity across chunk boundaries.
# Part of ai-train.py. Not standalone.

def persist_chunk(chunk_id: str, doc_id: str, source: str, category: str,
                  text: str, position: int, total_chunks: int,
                  llm=None) -> bool:
    """
    Thread-safe atomic append to JSONL store.

    Relationship tracking: every chunk knows its neighbors.
    Retrieval systems (ask_ai.py) can walk prev/next chain to reconstruct
    surrounding context when a single chunk doesn't contain enough information.

    Entity extraction only runs on position 0 (first chunk) to avoid
    redundant LLM calls — document-level entities don't change per chunk.
    """
    prev_chunk = f"{doc_id}_chunk_{position-1}" if position > 0 else None
    next_chunk = f"{doc_id}_chunk_{position+1}" if position < total_chunks - 1 else None

    # Entity extraction: first chunk only, only if flag enabled
    entities = []
    if llm and EXTRACT_ENTITIES and position == 0:
        entities = extract_entities(text, llm)

    entry = {
        "chunk_id": chunk_id,
        "doc_id": doc_id,
        "source": source,
        "category": category,
        "text": text,
        "position": position,
        "prev_chunk_id": prev_chunk,   # null for first chunk
        "next_chunk_id": next_chunk,   # null for last chunk
        "token_estimate": estimate_tokens(text),
        "entities": entities,
        "created_at": datetime.datetime.now().isoformat()
    }

    try:
        with MEMORY_LOCK:
            with open(DOCUMENT_STORE_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.error(f"Failed to persist chunk {chunk_id}: {e}")
        return False
