from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.candidate import Candidate
from app.services.document_parser import extract_text_from_file, parse_structured_data
from app.services.embedding_service import generate_embedding, add_to_faiss

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")
    
    text = await extract_text_from_file(file)
    if not text.strip():
        raise HTTPException(400, "Could not extract text from file")
    
    parsed = parse_structured_data(text)
    
    candidate = Candidate(
        name=Path(file.filename).stem,
        email=f"{Path(file.filename).stem.lower().replace(' ', '.')}@example.com",
        resume_text=text,
        skills=",".join(parsed.get("skills", []))
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
        "message": f"✅ {file.filename} processed successfully (any format)"
    }