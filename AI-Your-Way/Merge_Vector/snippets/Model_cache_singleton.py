# Demonstrates: Lazy-load singleton cache for the embedding model.
# SentenceTransformer models are 400-500MB and take 2-8 seconds to load.
# Loading on first request instead of at startup means the Flask server
# is immediately available — health checks pass before the model is warm.
# Part of merge_vector.py. Not standalone.

# Single approved model — locked at config level, not per-request
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"
EMBEDDING_MODEL_PATH = os.path.join(LOCAL_MODEL_DIR, EMBEDDING_MODEL_NAME)
EMBEDDING_DIM = 768

MODEL_CACHE = {}

def get_model() -> SentenceTransformer:
    """
    Loads the embedding model on first call and caches it for the process lifetime.

    Why lazy loading instead of loading at module import:
    - Flask server is immediately available (health checks pass before model loads)
    - Startup errors in the model load don't kill the entire process silently
    - Model path and name are validated at actual use time, not import time

    Why a dict cache instead of a module-level variable:
    - Module-level variables can be shadowed by test mocks without import tricks
    - Dict cache is explicit — MODEL_CACHE["model"] is inspectable in debug sessions
    - Supports future multi-model expansion (MODEL_CACHE["other_model"])

    Raises RuntimeError with the underlying cause — callers get a clear message
    instead of an AttributeError on None two stack frames later.
    """
    if "model" not in MODEL_CACHE:
        try:
            MODEL_CACHE["model"] = SentenceTransformer(EMBEDDING_MODEL_PATH)
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model from {EMBEDDING_MODEL_PATH}: {e}")
    return MODEL_CACHE["model"]
