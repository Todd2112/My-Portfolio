# Demonstrates: Full metadata preservation from Phase 1 JSONL into the vector index.
# Most vector pipelines embed the text and discard provenance. This parser
# carries every Phase 1 field through to the FAISS metadata blob so retrieval
# results include source, category, summary, and token counts — not just text.
# Part of merge_vector.py. Not standalone.

def parse_jsonl(path_or_file) -> list:
    """
    Parses Phase 1 JSONL output into (text, metadata) tuples.

    Accepts both file paths (str) and uploaded file objects (FileStorage),
    so the same parser handles both CLI and API ingestion paths.

    Metadata fields preserved per chunk:
    - doc_id      : document identifier from Phase 1
    - source      : original URL or filename
    - category    : classifier label (Healthcare, Technology, etc.)
    - created_at  : Phase 1 ingestion timestamp
    - summary     : LLM-generated summary from Phase 1 parser brain
    - total_tokens: token estimate from Phase 1

    Design decision: carry summary and total_tokens through explicitly.
    Early versions dropped these fields — retrieval results had no context
    about what the document contained or how large it was.
    Invalid JSON lines are skipped with a warning, not a fatal error.
    """
    documents = []

    if hasattr(path_or_file, "read"):
        lines = path_or_file.read().decode("utf-8").splitlines()
    else:
        with open(path_or_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

    for line_no, line in enumerate(lines, 1):
        try:
            j = json.loads(line)
            text = j.get("text", "").strip()
            if text:
                metadata = {
                    "doc_id":       j.get("doc_id", ""),
                    "source":       j.get("source", ""),
                    "category":     j.get("category", "General"),
                    "created_at":   j.get("created_at", ""),
                    "summary":      j.get("summary", ""),       # Phase 1 parser brain output
                    "total_tokens": j.get("total_tokens", 0)    # Phase 1 token estimate
                }
                documents.append((text, metadata))
        except Exception as e:
            print(f"[WARN] Skipping invalid JSON line {line_no}: {e}")  # skip, don't crash

    return documents
