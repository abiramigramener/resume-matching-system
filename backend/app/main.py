from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.features.candidates.router import router as candidates_router
from app.features.matching.router import router as matching_router
from app.features.candidates.embedding import load_faiss_index

app = FastAPI(title="Resume Matching System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
load_faiss_index()

app.include_router(candidates_router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(matching_router, prefix="/api/matching", tags=["Matching"])


@app.get("/")
def root():
    return {"message": "Resume Matching System is running!"}
