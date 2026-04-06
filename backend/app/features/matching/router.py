from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.candidates.model import Candidate
from app.features.candidates.embedding import generate_embedding, search_faiss
from app.features.candidates.parser import extract_skills
from app.features.matching.insights import generate_insights

router = APIRouter()

# Title → implied skills for short JD enrichment
_TITLE_SKILL_MAP = {
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


def _skill_score(job_skills: list, candidate_skills_str: str) -> float:
    if not job_skills:
        return 0.0
    candidate_skills = {s.strip() for s in candidate_skills_str.split(',') if s.strip()}
    return sum(1 for s in job_skills if s in candidate_skills) / len(job_skills)


def _enrich_jd(job_description: str) -> str:
    """Expand a short title-only JD with implied skills."""
    if len(job_description.strip().split()) >= 10:
        return job_description
    title_lower = job_description.lower()
    for keyword, implied in _TITLE_SKILL_MAP.items():
        if keyword in title_lower:
            return f"{job_description}\n\n{implied}"
    return job_description


@router.post("/match")
async def match_candidates(
    title: str = Form(...),
    description: str = Form(default=""),
    top_k: int = Form(default=10),
    db: Session = Depends(get_db),
):
    job_description = f"{title}\n\n{description}".strip()
    if not job_description:
        raise HTTPException(400, "Job description is required")

    candidates = db.query(Candidate).all()
    if not candidates:
        return {"matches": []}

    job_emb = generate_embedding(job_description)
    job_skills = extract_skills(job_description)
    faiss_map = dict(search_faiss(job_emb, [c.id for c in candidates], top_k=len(candidates)))

    results = []
    for candidate in candidates:
        faiss_raw = faiss_map.get(candidate.id, 0.0)
        skill_raw = _skill_score(job_skills, candidate.skills or "")
        blended = (faiss_raw * 0.5 + skill_raw * 0.5) if job_skills else faiss_raw
        results.append({
            "candidate": {
                "id": candidate.id, "name": candidate.name,
                "email": candidate.email, "phone": candidate.phone or "",
                "skills": candidate.skills or "", "filename": candidate.filename or "",
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
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        all_ids = [c.id for c in db.query(Candidate.id).all()]
        raise HTTPException(404, f"Candidate {candidate_id} not found. Available IDs: {all_ids}")

    effective_jd = _enrich_jd(job_description)

    try:
        insights = generate_insights(effective_jd, candidate.resume_text or "", score)
    except Exception as e:
        insights = {"summary": f"Could not generate insights: {e}",
                    "strengths": [], "weaknesses": [], "skill_gaps": [], "explanation": ""}

    return {"insights": insights}
