# Demonstrates: CAG (Cache-Augmented Generation) pattern learning.
# Accepted code changes are stored as learned patterns and retrieved by relevance scoring
# on future requests — giving the system persistent memory without retraining.
# Part of CAGMemory in my_coder.py. Not standalone.

def add_success(self, signature: str, user_intent: str, code_delta: str, confidence: float = 0.9):
    """
    Logs accepted code changes as learned patterns.
    Capped at 100 entries (rolling window) to prevent memory bloat.
    """
    with MEMORY_LOCK:
        self.learned.append({
            "id": datetime.datetime.now().strftime("%H%M%S"),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "signature": signature,
            "user_intent": user_intent,
            "code_delta": code_delta[:2000],
            "confidence": confidence
        })
        save_learning_log(self.learned)  # persists last 100 only


def get_relevant(self, query: str, k: int = 2) -> list:
    """
    Heuristic retrieval: scores patterns by intent match, signature match, and confidence.
    Intent match weighted 2x over signature match — user goal matters more than symbol name.
    Returns top-k patterns sorted by composite score.
    """
    q = query.lower()
    scored = []

    for entry in self.learned:
        score = (
            (2 if q in entry["user_intent"].lower() else 0) +  # intent match: weight 2
            (1 if q in entry["signature"].lower() else 0)       # signature match: weight 1
        )
        if score > 0:
            scored.append((score * entry.get("confidence", 0.5), entry))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [entry for _, entry in scored[:k]]
