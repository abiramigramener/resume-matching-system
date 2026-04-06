import json
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.features.candidates.model import Candidate
from app.features.candidates.parser import extract_text_from_file, parse_resume, extract_skill_details
from app.features.candidates.embedding import generate_embedding, add_to_faiss

router = APIRouter()

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", summary="Upload and parse a resume file")
async def upload_resume(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")

    # Extract raw text from the uploaded file (PDF, DOCX, image, etc.)
    text = await extract_text_from_file(file)
    if not text.strip():
        raise HTTPException(400, "Could not extract text from file")

    # Parse structured fields from raw text
    parsed = parse_resume(text)

    # Persist file to disk for later download
    safe_name = Path(file.filename).name
    await file.seek(0)
    with open(UPLOAD_DIR / safe_name, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Resolve identity fields — fall back to filename-based placeholders
    stem  = Path(file.filename).stem
    name  = parsed.get("name") or stem
    email = parsed.get("email") or f"{stem.lower().replace(' ', '.')}@example.com"

    # Reject duplicate: same email means same person / same file
    if db.query(Candidate).filter(Candidate.email == email).first():
        raise HTTPException(400, f"'{file.filename}' has already been uploaded.")

    candidate = Candidate(
        name=name,
        email=email,
        phone=parsed.get("phone"),
        resume_text=text,
        skills=",".join(parsed.get("skills", [])),
        skill_details=json.dumps(extract_skill_details(text)),
        total_experience_years=parsed.get("experience_years", 0.0),
        education=parsed.get("education"),
        education_details=json.dumps(parsed.get("education_details", [])),
        job_title=parsed.get("job_title"),
        filename=safe_name,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Index embedding for semantic search
    add_to_faiss(candidate.id, generate_embedding(text))

    return {
        "id": candidate.id,
        "name": candidate.name,
        "job_title": candidate.job_title,
        "experience_years": candidate.total_experience_years,
        "education": candidate.education,
        "skills_count": len(parsed.get("skills", [])),
        "filename": file.filename,
        "message": f"✅ {file.filename} processed successfully",
    }


@router.get("/download/{candidate_id}", summary="Download original resume file")
def download_resume(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate or not candidate.filename:
        raise HTTPException(404, "Resume file not found")

    file_path = UPLOAD_DIR / candidate.filename
    if not file_path.exists():
        raise HTTPException(404, "File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=candidate.filename,
        media_type="application/octet-stream",
    )


@router.get("/candidates", summary="List all uploaded candidates")
def list_candidates(db: Session = Depends(get_db)):
    """Returns structured candidate profiles — useful for recruiter dashboards."""
    candidates = db.query(Candidate).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "job_title": c.job_title,
            "experience_years": c.total_experience_years,
            "education": c.education,
            "skills": c.skills.split(",") if c.skills else [],
        }
        for c in candidates
    ]


class SkillEntry(BaseModel):
    name: str
    years: float = 0.0


class SkillsUpdateRequest(BaseModel):
    skills: List[SkillEntry]


@router.get("/{candidate_id}/skills", summary="Get structured skill details for a candidate")
def get_skills(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    # Return skill_details if available, else build from flat skills string
    if candidate.skill_details:
        try:
            return {"skills": json.loads(candidate.skill_details)}
        except (json.JSONDecodeError, TypeError):
            pass

    flat = [s.strip() for s in (candidate.skills or "").split(",") if s.strip()]
    return {"skills": [{"name": s, "years": 0.0} for s in flat]}


@router.put("/{candidate_id}/skills", summary="HR: update skill list and per-skill experience")
def update_skills(candidate_id: int, body: SkillsUpdateRequest, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    # Persist structured skill details
    skill_list = [{"name": s.name.strip(), "years": max(0.0, s.years)} for s in body.skills if s.name.strip()]
    candidate.skill_details = json.dumps(skill_list)
    # Keep flat skills in sync for matching logic
    candidate.skills = ",".join(s["name"] for s in skill_list)

    db.commit()
    db.refresh(candidate)
    return {"skills": skill_list, "message": "Skills updated successfully"}


class EducationEntry(BaseModel):
    degree: str
    field: str = ""
    institution: str = ""
    year: int = None


class EducationUpdateRequest(BaseModel):
    education: List[EducationEntry]


@router.get("/{candidate_id}/education", summary="Get structured education details")
def get_education(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    if candidate.education_details:
        try:
            return {"education": json.loads(candidate.education_details)}
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback: wrap flat education string
    return {"education": [{"degree": candidate.education or "", "field": "", "institution": "", "year": None}]}


@router.put("/{candidate_id}/education", summary="HR: update education details")
def update_education(candidate_id: int, body: EducationUpdateRequest, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    edu_list = [e.dict() for e in body.education if e.degree.strip()]
    candidate.education_details = json.dumps(edu_list)
    # Keep flat field in sync
    candidate.education = edu_list[0]["degree"] if edu_list else None

    db.commit()
    return {"education": edu_list, "message": "Education updated successfully"}
