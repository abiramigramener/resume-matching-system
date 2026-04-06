import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.candidates.model import Candidate
from app.features.candidates.parser import extract_text_from_file, parse_resume
from app.features.candidates.embedding import generate_embedding, add_to_faiss

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")

    text = await extract_text_from_file(file)
    if not text.strip():
        raise HTTPException(400, "Could not extract text from file")

    parsed = parse_resume(text)

    safe_name = Path(file.filename).name
    await file.seek(0)
    with open(UPLOAD_DIR / safe_name, "wb") as f:
        shutil.copyfileobj(file.file, f)

    stem = Path(file.filename).stem
    name = parsed.get("name") or stem
    email = parsed.get("email") or f"{stem.lower().replace(' ', '.')}@example.com"

    if not parsed.get("email"):
        existing = db.query(Candidate).filter(Candidate.email == email).first()
        if existing:
            email = f"{stem.lower().replace(' ', '.')}.{existing.id}@example.com"

    candidate = Candidate(
        name=name, email=email, phone=parsed.get("phone"),
        resume_text=text, skills=",".join(parsed.get("skills", [])),
        filename=safe_name,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    add_to_faiss(candidate.id, generate_embedding(text))

    return {"id": candidate.id, "filename": file.filename,
            "extracted_chars": len(text), "message": f"✅ {file.filename} processed successfully"}


@router.get("/download/{candidate_id}")
def download_resume(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate or not candidate.filename:
        raise HTTPException(404, "Resume file not found")
    file_path = UPLOAD_DIR / candidate.filename
    if not file_path.exists():
        raise HTTPException(404, "File not found on disk")
    return FileResponse(path=str(file_path), filename=candidate.filename,
                        media_type="application/octet-stream")
