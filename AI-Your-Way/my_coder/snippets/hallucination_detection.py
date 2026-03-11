# Demonstrates: Multi-layer confidence scoring to prevent hallucinated code from persisting to memory.
# Part of a larger validation pipeline in my_coder.py. Not standalone.

def detect_hallucinations(generated_code: str, original_code: str = "") -> dict:
    """
    Scores generated code confidence across five layers.
    Code below 0.6 confidence is flagged and blocked from memory persistence.
    """
    report = {
        "hallucination_detected": False,
        "confidence": 1.0,
        "issues": [],
        "safe_to_persist": True
    }

    # Layer 1: Syntax — fatal if broken
    syntax_ok, syntax_issues = check_syntax(generated_code)
    if not syntax_ok:
        report["hallucination_detected"] = True
        report["confidence"] = 0.0
        report["issues"].extend(syntax_issues)
        report["safe_to_persist"] = False
        return report

    # Layer 2: Placeholder detection — incomplete stubs penalized -0.3
    placeholder_issues = check_placeholders(generated_code)
    if placeholder_issues:
        report["hallucination_detected"] = True
        report["confidence"] -= 0.3
        report["issues"].extend(placeholder_issues)

    # Layer 3: Function preservation — missing functions penalized -0.4
    if original_code:
        orig_tree = ast.parse(original_code)
        new_tree = ast.parse(generated_code)
        orig_funcs = {n.name for n in ast.walk(orig_tree) if isinstance(n, ast.FunctionDef)}
        new_funcs = {n.name for n in ast.walk(new_tree) if isinstance(n, ast.FunctionDef)}
        missing_funcs = orig_funcs - new_funcs
        if missing_funcs:
            report["hallucination_detected"] = True
            report["confidence"] -= 0.4
            report["issues"].append(f"Missing functions: {missing_funcs}")

    # Layer 4: Import consistency — missing imports penalized -0.2
    import_issues = check_imports(generated_code, original_code)
    if import_issues:
        report["confidence"] -= 0.2
        report["issues"].extend(import_issues)

    # Layer 5: Infinite loop detection
    if re.search(r'while\s+True:', generated_code):
        if 'break' not in generated_code:
            report["hallucination_detected"] = True
            report["confidence"] -= 0.4
            report["issues"].append("Potential infinite loop: 'while True' without 'break'")

    report["confidence"] = max(0.0, report["confidence"])
    report["safe_to_persist"] = report["confidence"] >= 0.6 and not report["hallucination_detected"]

    return report
