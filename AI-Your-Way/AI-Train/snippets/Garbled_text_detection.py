# Demonstrates: Heuristic quality gate for PDF text extraction.
# Runs after every extraction attempt to catch corrupted output before it
# pollutes the knowledge base. Three independent signals catch different failure modes.
# Part of ai-train.py extraction pipeline. Not standalone.

def is_extraction_garbled(text: str, min_length: int = 100, max_symbol_ratio: float = 0.4) -> bool:
    """
    Detects gibberish extraction output using three independent heuristics.
    Called after every PDF extraction attempt before accepting the result.

    Heuristics:
    - Length gate: text too short for a multi-page document signals extraction failure
    - Symbol ratio: non-alphanumeric chars above 40% signals encoding corruption
    - Repeated pattern: 10+ consecutive identical chars signals scanned artifact noise
    
    Returns True if garbled (reject), False if valid (accept).
    """
    if not text or len(text.strip()) < min_length:
        return True

    alpha_count = sum(c.isalnum() or c.isspace() for c in text)
    total_chars = len(text)

    if total_chars == 0:
        return True

    symbol_ratio = (total_chars - alpha_count) / total_chars

    if symbol_ratio > max_symbol_ratio:
        return True  # encoding corruption — too many symbols

    if re.search(r'(.)\1{10,}', text):
        return True  # repeated character artifact — scanned PDF noise

    return False
