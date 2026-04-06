import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
from app.core.config import settings

_model = None
_index = None
_id_map: list = []  # position in FAISS index → candidate DB id


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def load_faiss_index() -> None:
    """Load persisted FAISS index and ID map from disk on startup."""
    global _index, _id_map
    if os.path.exists(settings.FAISS_INDEX_PATH) and os.path.exists(settings.FAISS_IDS_PATH):
        _index = faiss.read_index(settings.FAISS_INDEX_PATH)
        _id_map = list(np.load(settings.FAISS_IDS_PATH).tolist())
    else:
        _index = faiss.IndexFlatIP(settings.EMBEDDING_DIM)
        _id_map = []


def generate_embedding(text: str) -> np.ndarray:
    """Generate a normalized L2 embedding vector for the given text."""
    emb = _get_model().encode([text], normalize_embeddings=True)
    return emb[0].astype("float32")


def add_to_faiss(candidate_id: int, embedding: np.ndarray) -> None:
    """Add a candidate embedding to the FAISS index and persist to disk."""
    global _index, _id_map
    if _index is None:
        load_faiss_index()
    _index.add(np.array([embedding], dtype="float32"))
    _id_map.append(candidate_id)
    faiss.write_index(_index, settings.FAISS_INDEX_PATH)
    np.save(settings.FAISS_IDS_PATH, np.array(_id_map))


def search_faiss(query_emb: np.ndarray, candidate_ids: list, top_k: int = 10) -> list:
    """
    Search FAISS for the top-k most similar candidates.

    Returns list of (candidate_id, cosine_similarity_score) tuples.
    Score range: 0.0 – 1.0 (higher = more similar).
    Falls back to zero scores if index is empty.
    """
    if _index is None or _index.ntotal == 0:
        return [(cid, 0.0) for cid in candidate_ids[:top_k]]

    k = min(top_k, _index.ntotal)
    distances, indices = _index.search(np.array([query_emb], dtype="float32"), k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(_id_map):
            continue
        cid = _id_map[idx]
        if cid in candidate_ids:
            results.append((cid, float(dist)))
    return results
