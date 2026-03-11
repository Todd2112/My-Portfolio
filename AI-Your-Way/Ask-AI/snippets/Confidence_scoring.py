# Demonstrates: Weighted multi-signal confidence scoring.
# Five independent signals combined into one score — source type weighted
# most heavily because a direct KB answer is fundamentally more reliable
# than a web fallback regardless of other signal values.
# Part of ask_ai.py. Not standalone.

# Signal weights — must sum to 1.0
PHASE3_CONF_WEIGHTS = {
    "outcome": 0.35,   # source type: KB_DIRECT=1.0, KB_AUGMENTED=0.9, WEB=0.4, FAIL=-1.0
    "user":    0.25,   # user feedback: approve=1.0, edit=0.0, reject=-1.0
    "rag":     0.25,   # RAG consensus: 60th percentile similarity across snippets
    "rerank":  0.10,   # top rerank score from semantic reranker
    "stat":    0.05    # statistical baseline (always 0.5)
}

OUTCOME_MAP = {
    "KB_DIRECT":    1.0,   # answer from KB, no augmentation
    "KB_AUGMENTED": 0.9,   # answer from KB, refined by LLM (validated)
    "HIL_RECALL":   0.85,  # human-corrected answer recalled from memory
    "RAG":          0.7,   # synthesized from multiple snippets
    "WEB":          0.4,   # DuckDuckGo fallback
    "FAIL":        -1.0    # no answer found
}

def compute_confidence(signals: dict, weights: dict = PHASE3_CONF_WEIGHTS) -> float:
    """
    Weighted confidence score from five independent signals.

    All signals are normalized from [-1, 1] → [0, 1] before weighting.
    This allows negative signals (FAIL=-1.0, reject feedback=-1.0) to
    meaningfully drag the score down without requiring special-case logic.

    Returns final confidence in [0, 1].
    """
    score = 0.0

    for key, w in weights.items():
        val = signals.get(key, 0.0)
        # Normalize [-1, 1] → [0, 1]
        normalized = (max(-1.0, min(1.0, val)) + 1.0) / 2.0
        score += normalized * w

    return float(max(0.0, min(1.0, score)))
