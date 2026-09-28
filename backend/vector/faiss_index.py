"""Semantic vector index over catalog text (careers, courses, certifications, opportunities).

Uses FAISS when available for fast approximate search. Falls back to a plain
NumPy cosine-similarity scan otherwise -- correct and fast enough at MVP
catalog sizes, and it means the feature still works without the faiss
package installed. The relational database stays the source of truth; this
index only maps id -> similarity score.
"""

from __future__ import annotations

import numpy as np

from backend.ai.embeddings import encode


class VectorIndex:
    def __init__(self, name: str):
        self.name = name
        self._ids: list[int] = []
        self._vectors: np.ndarray | None = None
        self._faiss_index = None

    def build(self, ids: list[int], texts: list[str]) -> None:
        self._ids = list(ids)
        if not ids:
            self._vectors = None
            self._faiss_index = None
            return

        vectors = encode(texts)
        # Normalize so inner-product search behaves like cosine similarity.
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = (vectors / norms).astype("float32")
        self._vectors = normalized

        try:
            import faiss

            index = faiss.IndexFlatIP(normalized.shape[1])
            index.add(normalized)
            self._faiss_index = index
        except ImportError:
            self._faiss_index = None

    def search(self, query_text: str, top_k: int = 10) -> list[tuple[int, float]]:
        if not self._ids or self._vectors is None:
            return []

        query_vector = encode([query_text])[0]
        norm = np.linalg.norm(query_vector)
        if norm == 0:
            return []
        query_vector = (query_vector / norm).astype("float32")

        if self._faiss_index is not None:
            scores, indices = self._faiss_index.search(query_vector.reshape(1, -1), min(top_k, len(self._ids)))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue
                results.append((self._ids[idx], float(score)))
            return results

        similarities = self._vectors @ query_vector
        top_indices = np.argsort(-similarities)[:top_k]
        return [(self._ids[i], float(similarities[i])) for i in top_indices]

    @property
    def is_built(self) -> bool:
        return self._vectors is not None and len(self._ids) > 0


_registry: dict[str, VectorIndex] = {}


def get_index(name: str) -> VectorIndex:
    if name not in _registry:
        _registry[name] = VectorIndex(name)
    return _registry[name]
