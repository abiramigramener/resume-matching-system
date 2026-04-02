import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from app.services.document_parser import extract_skills

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def _compute_overlap(job_desc: str, resume_text: str):
    """
    Pre-compute skill overlap using the alias-aware extractor.
    Returns (job_skills, resume_skills, matched, gaps, extra).
    """
    job_skills = extract_skills(job_desc)
    resume_skills = extract_skills(resume_text)
    matched = [s for s in job_skills if s in resume_skills]
    gaps = [s for s in job_skills if s not in resume_skills]
    extra = [s for s in resume_skills if s not in job_skills]
    return job_skills, resume_skills, matched, gaps, extra


def generate_insights(job_desc: str, resume_text: str, score: float) -> dict:
    job_skills, resume_skills, matched, gaps, extra = _compute_overlap(job_desc, resume_text)

    if not os.getenv("GROQ_API_KEY"):
        return _local_insights(job_skills, resume_skills, matched, gaps, extra, score)

    try:
        prompt = f"""You are a senior technical recruiter. Analyze the candidate's fit for the job.

JOB DESCRIPTION:
{job_desc[:800]}

CANDIDATE RESUME:
{resume_text[:2000]}

SKILL ANALYSIS (pre-computed, use these exact values):
- Job requires: {job_skills}
- Candidate has: {resume_skills}
- Overlapping skills ({len(matched)}): {matched}
- Missing skills ({len(gaps)}): {gaps}
- Extra skills candidate has: {extra[:5]}
- Match score: {score:.1f}/100

Instructions:
- Use the overlapping skills list above — do NOT say 0 overlapping skills if the list is non-empty
- Be specific, mention actual skill names
- Return ONLY valid JSON, no markdown fences, no extra text

{{
  "summary": "2-3 sentence professional summary mentioning key matched skills",
  "strengths": ["specific strength with skill name", "strength 2", "strength 3"],
  "weaknesses": ["specific gap or weakness"],
  "skill_gaps": {json.dumps(gaps[:4]) if gaps else '["No critical gaps"]'},
  "overlapping_skills": {json.dumps(matched)},
  "match_reason": "1-2 sentences explaining the {score:.1f}% score using actual matched/missing skills",
  "explanation": "Detailed explanation referencing matched skills: {', '.join(matched[:5]) if matched else 'general experience'}"
}}"""

        response = _get_client().chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=900,
        )

        content = response.choices[0].message.content.strip()
        # Strip markdown fences
        content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)

        result = json.loads(content)
        # Always enforce pre-computed values so LLM can't hallucinate wrong counts
        result["overlapping_skills"] = matched
        result["skill_gaps"] = gaps[:4] if gaps else ["No critical gaps"]
        return result

    except json.JSONDecodeError:
        return _local_insights(job_skills, resume_skills, matched, gaps, extra, score)
    except Exception as e:
        print(f"Groq error: {e}")
        return _local_insights(job_skills, resume_skills, matched, gaps, extra, score)


def _local_insights(job_skills, resume_skills, matched, gaps, extra, score: float) -> dict:
    """Rule-based fallback — uses pre-computed overlap, never shows wrong counts."""
    n_matched = len(matched)
    n_required = len(job_skills)

    if score >= 70:
        summary = (
            f"Strong candidate matching {n_matched}/{n_required} required skills"
            + (f": {', '.join(matched[:3])}." if matched else ".")
        )
    elif score >= 40:
        summary = (
            f"Moderate match with {n_matched}/{n_required} required skills"
            + (f" including {', '.join(matched[:3])}." if matched else ".")
            + " Some gaps exist but candidate shows potential."
        )
    else:
        summary = (
            f"Low match with {n_matched}/{n_required} required skills."
            + (f" Candidate has: {', '.join(matched[:3])}." if matched else "")
            + " Significant gaps compared to job requirements."
        )

    return {
        "summary": summary,
        "strengths": matched[:4] if matched else ["General domain experience"],
        "weaknesses": [f"Missing required skill: {s}" for s in gaps[:2]] if gaps else ["No major weaknesses detected"],
        "skill_gaps": gaps[:4] if gaps else ["No critical gaps found"],
        "overlapping_skills": matched,
        "match_reason": (
            f"{n_matched} of {n_required} required skills matched"
            + (f" ({', '.join(matched[:3])})" if matched else "")
            + f", giving a {score:.1f}% score."
        ),
        "explanation": (
            f"Score: {score:.1f}% — matched {n_matched}/{n_required} required skills."
            + (f" Matched: {', '.join(matched)}." if matched else "")
            + (f" Missing: {', '.join(gaps[:3])}." if gaps else "")
            + (f" Extra skills: {', '.join(extra[:3])}." if extra else "")
        ),
    }
