import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

_model = None
_index = None
_id_map = []  # maps faiss position -> candidate id

FAISS_PATH = "faiss_index.bin"
IDMAP_PATH = "faiss_ids.npy"
DIM = 384


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def load_faiss_index():
    global _index, _id_map
    if os.path.exists(FAISS_PATH) and os.path.exists(IDMAP_PATH):
        _index = faiss.read_index(FAISS_PATH)
        _id_map = list(np.load(IDMAP_PATH).tolist())
    else:
        _index = faiss.IndexFlatIP(DIM)
        _id_map = []


def generate_embedding(text: str) -> np.ndarray:
    model = _get_model()
    emb = model.encode([text], normalize_embeddings=True)
    return emb[0].astype("float32")


def add_to_faiss(candidate_id: int, embedding: np.ndarray):
    global _index, _id_map
    if _index is None:
        load_faiss_index()
    vec = np.array([embedding], dtype="float32")
    _index.add(vec)
    _id_map.append(candidate_id)
    faiss.write_index(_index, FAISS_PATH)
    np.save(IDMAP_PATH, np.array(_id_map))


def search_faiss(query_emb: np.ndarray, candidate_ids: list, top_k: int = 10):
    """Returns list of (candidate_id, score) tuples."""
    if _index is None or _index.ntotal == 0:
        # fallback: return all candidates with score 0
        return [(cid, 0.0) for cid in candidate_ids[:top_k]]

    k = min(top_k, _index.ntotal)
    query = np.array([query_emb], dtype="float32")
    distances, indices = _index.search(query, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(_id_map):
            continue
        cid = _id_map[idx]
        if cid in candidate_ids:
            results.append((cid, float(dist)))
    return results
