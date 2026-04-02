from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def generate_insights(job_desc: str, resume_text: str, score: float):
    client = _get_client()
    
    # If no API key, return mock insights
    if not client:
        return """{
  "summary": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable for AI-powered insights.",
  "strengths": ["Match score calculated using semantic similarity"],
  "weaknesses": ["AI insights unavailable without API key"],
  "skill_gaps": ["Configure OpenAI API for detailed analysis"],
  "explanation": "Semantic matching is working. Add OpenAI API key for detailed insights."
}"""
    
    prompt = f"""You are an expert recruiter.
Job: {job_desc[:500]}
Candidate Resume: {resume_text[:1500]}
Match Score: {score}/100

Generate JSON:
{{
  "summary": "2-sentence overview",
  "strengths": ["bullet1", "bullet2"],
  "weaknesses": ["bullet1"],
  "skill_gaps": ["gap1"],
  "explanation": "Why this score?"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content