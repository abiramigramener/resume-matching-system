from app.services.embedding_service import generate_embedding, search_faiss
from app.database import SessionLocal
from app.models.candidate import Candidate


def hybrid_match(job_description: str, top_k: int = 10):
    db = SessionLocal()
    candidates = db.query(Candidate).all()
    db.close()

    if not candidates:
        return []

    job_emb = generate_embedding(job_description)
    candidate_ids = [c.id for c in candidates]
    scores = search_faiss(job_emb, candidate_ids, top_k=top_k)

    results = []
    for cand_id, score in scores:
        candidate = next((c for c in candidates if c.id == cand_id), None)
        if candidate:
            results.append({"candidate": candidate, "score": round(score * 100, 2)})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
