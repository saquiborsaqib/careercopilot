"""Semantic embedding service.

Uses Sentence Transformers when the model can be loaded (installed + weights
available). Falls back to a scikit-learn HashingVectorizer, which needs no
network access or fitted corpus, so semantic matching keeps working even in
offline / constrained environments. Callers only depend on `encode`, so the
fallback is transparent to the rest of the app.
"""

from __future__ import annotations

import threading

import numpy as np

from backend.core.config import settings

_lock = threading.Lock()
_model = None
_model_load_attempted = False
_fallback_vectorizer = None


def _try_load_sentence_transformer():
    global _model, _model_load_attempted
    if _model_load_attempted:
        return _model
    _model_load_attempted = True
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.embedding_model)
    except Exception:
        _model = None
    return _model


def _get_fallback_vectorizer():
    global _fallback_vectorizer
    if _fallback_vectorizer is None:
        from sklearn.feature_extraction.text import HashingVectorizer

        _fallback_vectorizer = HashingVectorizer(n_features=512, alternate_sign=False, norm="l2")
    return _fallback_vectorizer


def encode(texts: list[str]) -> np.ndarray:
    """Encode a list of texts into a 2D float32 embedding matrix."""
    if not texts:
        return np.zeros((0, 1), dtype="float32")

    with _lock:
        model = _try_load_sentence_transformer()
        if model is not None:
            vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return np.asarray(vectors, dtype="float32")

        vectorizer = _get_fallback_vectorizer()
        matrix = vectorizer.transform(texts)
        return matrix.toarray().astype("float32")


def embedding_backend() -> str:
    with _lock:
        model = _try_load_sentence_transformer()
        return "sentence-transformers" if model is not None else "hashing-vectorizer-fallback"


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vector_a, vector_b) / (norm_a * norm_b))


def semantic_similarity(text_a: str, text_b: str) -> float:
    """Return a 0..1 similarity score between two pieces of text."""
    if not text_a.strip() or not text_b.strip():
        return 0.0
    vectors = encode([text_a, text_b])
    similarity = cosine_similarity(vectors[0], vectors[1])
    # Clamp: hashing-vectorizer cosine similarity is already in [0, 1] for
    # non-negative vectors; sentence-transformer cosine can dip slightly
    # negative for unrelated text, so clamp to a usable [0, 1] range.
    return max(0.0, min(1.0, similarity))
