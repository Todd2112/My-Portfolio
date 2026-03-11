# Demonstrates: AST-aware semantic chunking for RAG indexing.
# One function/class = one chunk. Preserves syntactic boundaries instead of splitting mid-function.
# Part of RAGEngine in my_coder.py. Not standalone.

def _chunk_by_ast(self, code_text: str) -> list:
    """
    Splits code at function/class boundaries using the AST.
    Falls back to character-based chunking if parsing fails.
    """
    try:
        tree = ast.parse(code_text)
    except SyntaxError:
        return [{"text": chunk, "type": "fallback", "name": "unknown", "importance": 0.5}
                for chunk in self._chunk_text(code_text)]

    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            # Skip nested functions/methods — top-level only
            parent = getattr(node, 'parent', None)
            if parent and isinstance(parent, (ast.FunctionDef, ast.ClassDef)):
                continue

            chunk_text = ast.get_source_segment(code_text, node)
            if not chunk_text:
                continue

            chunks.append({
                "text": chunk_text,
                "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                "name": node.name,
                "importance": self._calculate_importance(node, code_text),
                "start_line": node.lineno,
                "end_line": getattr(node, 'end_lineno', node.lineno)
            })

    return chunks or [{"text": chunk, "type": "fallback", "name": "module", "importance": 0.5}
                      for chunk in self._chunk_text(code_text)]


def _calculate_importance(self, node, full_code: str) -> float:
    """
    Weights each chunk for retrieval priority.
    Factors: docstring presence, code length, reference frequency in codebase.
    """
    importance = 0.5  # base

    if ast.get_docstring(node):
        importance += 0.2  # documented code ranks higher

    try:
        lines = len(ast.get_source_segment(full_code, node).splitlines())
        importance += min(0.3, lines / 100)  # longer = more substantial
    except:
        pass

    if hasattr(node, 'name'):
        ref_count = full_code.count(node.name)
        importance += min(0.2, ref_count / 20)  # frequently referenced = more important

    return min(1.0, importance)
