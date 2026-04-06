from sqlalchemy import Column, Integer, String, Text, Float
from app.core.database import Base


class Candidate(Base):
    """
    Stores a parsed candidate profile extracted from an uploaded resume.

    Field guide
    -----------
    resume_text         Raw text extracted from the uploaded file.
                        Used for: semantic embeddings, full-text search, LLM prompts.
                        NOT intended for direct display — use structured fields instead.

    skills              Comma-separated list of canonical skill names detected in the resume.
                        Example: "python,machine learning,sql,docker"
                        Populated by extract_skills() using SKILL_ALIASES.

    total_experience_years
                        Total years of professional experience parsed from resume text.
                        Extracted via regex patterns like "5+ years of experience".

    education           Highest education level detected (e.g. "Bachelor", "Master", "Phd").
                        Extracted from keywords in resume text.

    job_title           Primary/most recent job title extracted from the resume.
                        Used for title-based matching and display.

    filename            Original uploaded filename, used to serve the file for download.
    """

    __tablename__ = "candidates"

    # ── Identity ──────────────────────────────────────────────────────────────
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String, index=True, nullable=True,
                   comment="Full name extracted from resume header")
    email = Column(String, unique=True, index=True, nullable=True,
                   comment="Email extracted from resume; used as unique identifier")
    phone = Column(String, nullable=True,
                   comment="Phone number extracted from resume")

    # ── Raw content (for embeddings / LLM) ───────────────────────────────────
    resume_text = Column(Text, nullable=True,
                         comment="Full raw text extracted from the uploaded file. "
                                 "Used for semantic search embeddings and AI insight generation.")

    # ── Structured parsed fields (for filtering / display) ───────────────────
    skills = Column(Text, nullable=True,
                    comment="Comma-separated canonical skill names. "
                             "Example: 'python,machine learning,docker'")

    skill_details = Column(Text, nullable=True,
                           comment="JSON array of {name, years} objects for per-skill experience. "
                                   "Example: '[{\"name\":\"Python\",\"years\":3},{\"name\":\"SQL\",\"years\":5}]'. "
                                   "HR-editable. Takes precedence over skills field when present.")

    total_experience_years = Column(Float, default=0.0, nullable=False,
                                    comment="Total years of professional experience parsed from resume")

    education = Column(String, nullable=True,
                       comment="Highest education level detected: Bachelor / Master / Phd / B.Tech etc.")

    job_title = Column(String, nullable=True, index=True,
                       comment="Primary job title extracted from resume (e.g. 'Data Scientist', 'Civil Engineer')")

    # ── File reference ────────────────────────────────────────────────────────
    filename = Column(String, nullable=True,
                      comment="Uploaded filename used to serve the resume file for download")
