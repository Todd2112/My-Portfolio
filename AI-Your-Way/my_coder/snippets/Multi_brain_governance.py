# Demonstrates: Role-specific governance enforcement baked into each LLM brain at the prompt level.
# Each brain receives a different system prompt, token limit, and temperature matching its task type.
# Paired with Modelfiles that set sampling parameters at the model serving layer.
# Part of MultiLLMManager in my_coder.py. Not standalone.

# Sampling parameters per brain (set in Modelfiles, enforced here at prompt level):
#   SOVEREIGN_CODER   — temperature 0.2  (consistent code generation)
#   FORENSIC_AUDITOR  — temperature 0.0  (fully deterministic validation)
#   MAVERICK          — temperature 0.3  (flexible intent classification)

TOKEN_LIMITS = {
    "coding": 4096,
    "reasoning": 1024,
    "organizer": 512
}

def _apply_governance(self, brain: str) -> str:
    """
    Injects role-appropriate constraints into every LLM call.
    Prevents preambles, enforces output format, and caps token usage per role.
    """
    max_tokens = TOKEN_LIMITS.get(brain, 512)

    if brain == "coding":
        return (
            f"ROLE: {brain.upper()}\n"
            f"MAX_OUTPUT: {max_tokens} tokens\n"
            "MAVERICK STYLE RULES:\n"
            "1. EVERY block must be labeled: '# Block X.Y: Description'\n"
            "2. ALL code MUST be wrapped in markdown blocks (```python ... ```)\n"
            "3. Use 4 spaces for indentation. No 'pass' or 'TODO' statements.\n"
            "FORBIDDEN: Preambles, apologies, markdown chatter.\n"
            "REQUIRED: Code first, explanation never (unless asked).\n"
            "USER REQUEST: "
        )

    elif brain == "reasoning":
        return (
            "ROLE: FORENSIC CODE AUDITOR\n"
            "TASK: Validate code for correctness and completeness.\n"
            "CHECK FOR: Syntax errors, placeholders (pass/TODO), truncated implementations.\n"
            "OUTPUT: 'PASS' or 'FAIL: <specific issue>'\n"
            "FORBIDDEN: Preambles, apologies, suggestions.\n"
        )

    return (
        f"ROLE: {brain.upper()}\n"
        f"MAX_OUTPUT: {max_tokens} tokens\n"
        "FORBIDDEN: Preambles, apologies, markdown chatter.\n"
        "USER REQUEST: "
    )

def _validate_output(self, brain: str, output: str, max_tokens: int) -> dict:
    """
    Programmatically verifies the LLM followed governance rules post-generation.
    Catches violations that slipped through the system prompt.
    """
    violations = []

    if brain == "coding":
        if not re.search(r"# Block \d+\.\d+", output):
            violations.append("Missing block labeling (# Block X.Y)")
        if "import " in output and output.find("import ") > 300:
            violations.append("Imports must appear at top of output")

    forbidden_starts = ["I understand", "Let me help", "Sure", "Certainly",
                        "Here is", "I apologize", "Sorry"]
    if any(output.strip().lower().startswith(p.lower()) for p in forbidden_starts):
        violations.append("Forbidden preamble detected")

    return {"valid": len(violations) == 0, "violations": violations}
