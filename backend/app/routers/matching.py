from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.candidate import Candidate
from app.services.embedding_service import generate_embedding, search_faiss
from app.services.insight_service import generate_insights

router = APIRouter()

@router.post("/match")
async def match_candidates(
    title: str = Form(...),
    description: str = Form(default=""),
    required_experience: int = Form(default=0),
    top_k: int = Form(default=10),
    db: Session = Depends(get_db)
):
    # Combine title and description for matching
    job_description = f"{title}\n\n{description}".strip()
    
    if not job_description:
        raise HTTPException(400, "Job title and description are required")

    candidates = db.query(Candidate).all()
    if not candidates:
        return {"matches": []}

    job_emb = generate_embedding(job_description)
    candidate_ids = [c.id for c in candidates]
    scores = search_faiss(job_emb, candidate_ids, top_k=top_k)

    results = []
    for cand_id, score in scores:
        candidate = next((c for c in candidates if c.id == cand_id), None)
        if not candidate:
            continue
        results.append({
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "skills": candidate.skills or "",
                "resume_text": candidate.resume_text or ""
            },
            "score": round(score * 100, 2),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return {"matches": results}


@router.post("/insights")
async def get_insights(
    job_description: str = Form(...),
    candidate_id: int = Form(...),
    score: float = Form(default=0.0),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    try:
        insights = generate_insights(job_description, candidate.resume_text or "", score)
    except Exception as e:
        insights = f"Could not generate insights: {e}"

    return {"insights": insights}
