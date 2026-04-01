from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_insights(job_desc: str, resume_text: str, score: float):
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