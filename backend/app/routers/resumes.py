import os
import shutil
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.candidate import Candidate
from app.services.document_parser import extract_text_from_file, parse_structured_data
from app.services.embedding_service import generate_embedding, add_to_faiss

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

    parsed = parse_structured_data(text)

    # Save file to disk
    safe_name = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_name
    await file.seek(0)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Use extracted email if found, else generate placeholder
    extracted_email = parsed.get("email")
    extracted_name = parsed.get("name")
    stem = Path(file.filename).stem
    name = extracted_name or stem
    email = extracted_email or f"{stem.lower().replace(' ', '.')}@example.com"

    # Handle duplicate email only if it's a generated placeholder (real emails are unique per person)
    if not extracted_email:
        existing = db.query(Candidate).filter(Candidate.email == email).first()
        if existing:
            email = f"{stem.lower().replace(' ', '.')}.{existing.id}@example.com"

    candidate = Candidate(
        name=name,
        email=email,
        phone=parsed.get("phone"),
        resume_text=text,
        skills=",".join(parsed.get("skills", [])),
        filename=safe_name,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    embedding = generate_embedding(text)
    add_to_faiss(candidate.id, embedding)

    return {
        "id": candidate.id,
        "filename": file.filename,
        "extracted_chars": len(text),
        "message": f"✅ {file.filename} processed successfully",
    }


@router.get("/download/{candidate_id}")
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
