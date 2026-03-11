# Demonstrates: Goal-based keyword filtering for targeted ingestion.
# Filters chunks to only those relevant to the user's stated goal before
# persistence — reduces noise in the knowledge base without LLM overhead.
# Part of ai-train.py. Not standalone.

def filter_chunks_by_goal(chunks: list, goal: str) -> list:
    """
    Pure keyword relevance filter — no LLM required.

    Extracts 3+ character words from the user's goal, then keeps only chunks
    containing at least one goal keyword. Returns original chunk list unmodified
    if filtering would produce an empty result (fail-safe).

    Design decision: keyword matching over semantic similarity here because:
    - This runs on every chunk before persistence (latency matters)
    - Goal terms are explicit and literal — "CPT codes", "billing", "ICD-10"
    - Semantic search is reserved for retrieval time (ask_ai.py)
    """
    if not goal or not chunks:
        return chunks

    goal_keywords = set(
        word.lower() for word in re.findall(r'\b\w{3,}\b', goal)
    )

    if not goal_keywords:
        return chunks

    filtered = [
        chunk for chunk in chunks
        if any(keyword in chunk.lower() for keyword in goal_keywords)
    ]

    return filtered if filtered else chunks  # never return empty — fail safe
