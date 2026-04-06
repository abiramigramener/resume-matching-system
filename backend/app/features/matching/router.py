import re
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.candidates.model import Candidate
from app.features.candidates.embedding import generate_embedding, search_faiss
from app.features.candidates.parser import extract_skills
from app.features.matching.insights import generate_insights
from app.shared.skills import DOMAIN_KEYWORDS

router = APIRouter()

# Weights — must sum to 1.0
W_SEMANTIC = 0.30   # FAISS cosine similarity
W_SKILLS   = 0.45   # skill overlap (Jaccard against job skills)
W_TITLE    = 0.25   # job title / domain match against resume text

# If skill overlap is 0 AND title match is 0, cap the final score
ZERO_MATCH_CAP = 0.20   # 20% max when completely unrelated

# Title → implied skills for short JD enrichment
_TITLE_SKILL_MAP = {
    "data scien":       "python sql machine learning data analysis pandas numpy scikit-learn statistics",
    "machine learning": "python machine learning deep learning scikit-learn tensorflow pytorch statistics",
    "data engineer":    "python sql spark hadoop airflow kafka aws",
    "frontend":         "javascript react vue angular html css typescript",
    "backend":          "python java sql rest api docker kubernetes",
    "devops":           "docker kubernetes aws ci/cd linux terraform jenkins",
    "nlp":              "python nlp natural language processing transformers bert pytorch",
    "computer vision":  "python computer vision tensorflow pytorch deep learning",
    "full stack":       "javascript react vue node sql html css rest api",
    "analyst":          "sql python data analysis excel tableau power bi statistics",
    "civil engineer":   "civil engineering autocad staad pro structural design construction management surveying",
    "mechanical":       "mechanical engineering solidworks autocad manufacturing thermodynamics",
    "electrical":       "electrical engineering plc scada power systems circuit design",
}


def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip()


def _skill_score(job_skills: list, candidate_skills_str: str) -> float:
    """Fraction of job-required skills present in candidate profile (case-insensitive)."""
    if not job_skills:
        return 0.0
    candidate_skills = {s.strip().lower() for s in candidate_skills_str.split(',') if s.strip()}
    job_skills_lower = {s.lower() for s in job_skills}
    matched = sum(1 for s in job_skills_lower if s in candidate_skills)
    return matched / len(job_skills)


def _extract_jd_skills(job_description: str) -> list[str]:
    """
    Extract skills from a job description using two strategies:

    1. Run the resume skill extractor (handles SKILLS sections + alias matching)
    2. If that returns nothing, treat the JD as a raw skill list —
       split by commas/newlines and use each token as a skill term.
       This handles JDs like "Coronary Angiography, PCI, Echocardiography"
       that have no section header and no alias match.
    """
    from app.features.candidates.parser import extract_skills as _extract
    skills = _extract(job_description)
    if skills:
        return skills

    # Fallback: parse raw comma/newline-separated skill list
    raw = re.split(r'[,\n;]', job_description)
    fallback = []
    for item in raw:
        item = item.strip().strip('.-•')
        if 1 <= len(item.split()) <= 6 and len(item) >= 2 and not item.isdigit():
            fallback.append(item)
    return list(dict.fromkeys(fallback))


def _title_score(job_title: str, resume_text: str) -> float:
    """
    Score how well the job title / domain matches the resume.
    Checks DOMAIN_KEYWORDS first (structured), then falls back to
    direct keyword presence in resume text.
    """
    title_lower = _normalize(job_title)
    resume_lower = _normalize(resume_text)

    # 1. Check structured domain map
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if domain in title_lower or any(kw in title_lower for kw in keywords):
            # Count how many domain keywords appear in the resume
            hits = sum(1 for kw in keywords if kw in resume_lower)
            if hits > 0:
                return min(1.0, hits / max(len(keywords) * 0.4, 1))

    # 2. Fallback: check if individual title words appear in resume
    title_words = [w for w in title_lower.split() if len(w) > 3
                   and w not in {"senior", "junior", "lead", "manager", "engineer",
                                 "specialist", "analyst", "associate", "principal"}]
    if not title_words:
        return 0.0
    hits = sum(1 for w in title_words if w in resume_lower)
    return hits / len(title_words)


def _enrich_jd(job_description: str) -> str:
    """Expand a short title-only JD with implied skills for insights."""
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

    # Enrich short JDs before embedding so semantic search is more accurate
    enriched_jd = _enrich_jd(job_description)

    job_emb = generate_embedding(enriched_jd)
    job_skills = _extract_jd_skills(job_description)  # use raw JD, not enriched, for skill matching
    faiss_map = dict(search_faiss(job_emb, [c.id for c in candidates], top_k=len(candidates)))

    results = []
    for candidate in candidates:
        semantic = faiss_map.get(candidate.id, 0.0)          # 0–1
        skill    = _skill_score(job_skills, candidate.skills or "")  # 0–1
        title_m  = _title_score(title, candidate.resume_text or "")  # 0–1

        # Weighted blend
        if job_skills:
            blended = (semantic * W_SEMANTIC) + (skill * W_SKILLS) + (title_m * W_TITLE)
        else:
            # No skills in JD — rely on semantic + title only
            blended = (semantic * 0.55) + (title_m * 0.45)

        # Penalty: cap score when there's no meaningful match at all
        if skill == 0.0 and title_m == 0.0:
            blended = min(blended, ZERO_MATCH_CAP)

        # Compute matched vs unmatched skills — case-insensitive comparison
        candidate_skills_list = [s.strip() for s in (candidate.skills or "").split(",") if s.strip()]
        job_skill_set_lower = {s.lower() for s in job_skills}
        matched_skills  = [s for s in candidate_skills_list if s.lower() in job_skill_set_lower]
        unmatched_skills = [s for s in candidate_skills_list if s.lower() not in job_skill_set_lower]

        results.append({
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "phone": candidate.phone or "",
                "skills": candidate.skills or "",
                "matched_skills": [s.strip() for s in matched_skills],
                "unmatched_skills": [s.strip() for s in unmatched_skills],
                "filename": candidate.filename or "",
                "job_title": candidate.job_title or "",
                "experience_years": candidate.total_experience_years or 0,
                "education": candidate.education or "",
            },
            "score": round(blended * 100, 2),
            "score_breakdown": {
                "semantic": round(semantic * 100, 1),
                "skills":   round(skill * 100, 1),
                "title":    round(title_m * 100, 1),
            },
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    filtered = [r for r in results if r["score"] >= 60]
    return {"matches": filtered[:top_k]}


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
