# Demonstrates: Multi-brain intent routing with high-weight keyword bypass.
# Deterministic paths short-circuit LLM classification for known patterns,
# falling back to the organizer brain (1B model) only for ambiguous input.
# Part of my_coder.py. Not standalone.

# High-confidence keyword triggers — bypass LLM classification entirely
AUDIT_KEYWORDS = ["audit", "review", "validate", "check for errors", "find errors"]
MODIFY_KEYWORDS = ["modify-target:", "system override"]

def detect_intent(user_input: str) -> tuple:
    """
    Routes requests to the appropriate brain.
    Priority: deterministic keyword match > LLM classification fallback.

    Returns: (intent_string, optional_target)
    """
    user_lower = user_input.lower()

    # High-weight bypass: audit/review triggers never need LLM classification
    if any(word in user_lower for word in AUDIT_KEYWORDS):
        return "review", None

    # Explicit modify-target override
    for keyword in MODIFY_KEYWORDS:
        if keyword in user_lower:
            target = user_lower.split("modify-target:")[-1].split()[0].strip() \
                     if "modify-target:" in user_lower else "default_target"
            return "modify-target", target

    # Fallback: organizer brain (1B, temp 0.3) classifies ambiguous input
    prompt = f"""Classify into ONE keyword: modify-target, retrieve, review, fix, explain, general.
Format: KEYWORD or KEYWORD:TARGET
Query: {user_input}"""

    response = llm_manager.generate("organizer", prompt, max_tokens=512)
    parts = response.strip().split(":", 1)
    intent = parts[0].strip().lower()
    target = parts[1].strip() if len(parts) > 1 else None

    if intent not in ["modify-target", "retrieve", "review", "fix", "explain", "general"]:
        intent = "general"

    return intent, target
