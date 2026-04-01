from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import resumes, jobs, matching
import os
from app.services.embedding_service import load_faiss_index

app = FastAPI(title="Resume Matching System")

# CORS for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Load FAISS on startup
load_faiss_index()

app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(matching.router, prefix="/api/matching", tags=["Matching"])

@app.get("/")
def root():
    return {"message": "Resume Matching System is running! 🚀"}