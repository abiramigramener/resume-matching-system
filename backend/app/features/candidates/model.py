from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    resume_text = Column(Text)
    skills = Column(Text)
    filename = Column(String, nullable=True)
