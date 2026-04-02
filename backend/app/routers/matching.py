from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.candidate import Candidate
from app.services.embedding_service import generate_embedding, search_faiss
from app.services.insight_service import generate_insights
from app.services.document_parser import extract_skills

router = APIRouter()


def _skill_score(job_skills: list, candidate_skills_str: str) -> float:
    """Jaccard-style skill overlap score (0.0 - 1.0)."""
    if not job_skills:
        return 0.0
    candidate_skills = set(s.strip() for s in candidate_skills_str.split(',') if s.strip())
    matched = sum(1 for s in job_skills if s in candidate_skills)
    return matched / len(job_skills)


@router.post("/match")
async def match_candidates(
    title: str = Form(...),
    description: str = Form(default=""),
    top_k: int = Form(default=10),
    db: Session = Depends(get_db)
):
    job_description = f"{title}\n\n{description}".strip()
    if not job_description:
        raise HTTPException(400, "Job description is required")

    candidates = db.query(Candidate).all()
    if not candidates:
        return {"matches": []}

    job_emb = generate_embedding(job_description)
    job_skills = extract_skills(job_description)
    candidate_ids = [c.id for c in candidates]
    faiss_scores = search_faiss(job_emb, candidate_ids, top_k=len(candidates))

    # Build a lookup for faiss scores
    faiss_map = {cid: score for cid, score in faiss_scores}

    results = []
    for candidate in candidates:
        faiss_raw = faiss_map.get(candidate.id, 0.0)  # 0.0 - 1.0 (cosine similarity)
        skill_raw = _skill_score(job_skills, candidate.skills or "")

        # Blend: 50% semantic + 50% skill overlap (when job has skills)
        # If no skills detected in JD, fall back to pure semantic
        if job_skills:
            blended = (faiss_raw * 0.5) + (skill_raw * 0.5)
        else:
            blended = faiss_raw

        results.append({
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "phone": candidate.phone or "",
                "skills": candidate.skills or "",
                "filename": candidate.filename or "",
            },
            "score": round(blended * 100, 2),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return {"matches": results[:top_k]}


@router.post("/insights")
async def get_insights(
    job_description: str = Form(...),
    candidate_id: int = Form(...),
    score: float = Form(default=0.0),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        all_ids = [c.id for c in db.query(Candidate.id).all()]
        raise HTTPException(404, f"Candidate {candidate_id} not found. Available IDs: {all_ids}")

    # If job_description is very short (just a title), enrich it with
    # the candidate's resume text so skill overlap can still be computed
    # using the candidate's own skills as the reference baseline
    effective_jd = job_description
    if len(job_description.strip().split()) < 10:
        # Short title only — append common skills implied by the title
        title_lower = job_description.lower()
        title_skill_map = {
            "data scien": "python sql machine learning data analysis data visualization pandas numpy scikit-learn statistics",
            "machine learning": "python machine learning deep learning scikit-learn tensorflow pytorch statistics feature engineering",
            "data engineer": "python sql spark hadoop airflow kafka aws data engineering",
            "frontend": "javascript react vue angular html css typescript",
            "backend": "python java sql rest api docker kubernetes",
            "devops": "docker kubernetes aws ci/cd linux terraform jenkins",
            "nlp": "python nlp natural language processing transformers bert pytorch tensorflow",
            "computer vision": "python computer vision tensorflow pytorch deep learning",
            "full stack": "javascript react vue node sql html css rest api",
            "analyst": "sql python data analysis excel tableau power bi statistics",
        }
        for keyword, implied_skills in title_skill_map.items():
            if keyword in title_lower:
                effective_jd = f"{job_description}\n\n{implied_skills}"
                break

    try:
        insights = generate_insights(effective_jd, candidate.resume_text or "", score)
    except Exception as e:
        insights = {"summary": f"Could not generate insights: {e}", "strengths": [], "weaknesses": [], "skill_gaps": [], "explanation": ""}

    return {"insights": insights}
