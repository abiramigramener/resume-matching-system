import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from app.features.candidates.parser import extract_skills

load_dotenv()
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def _compute_overlap(job_desc: str, resume_text: str):
    """
    Compute skill overlap between JD and resume.
    Uses fallback extraction for JDs that are raw skill lists (no section headers).
    """
    from app.features.matching.router import _extract_jd_skills
    job_skills = _extract_jd_skills(job_desc)
    resume_skills = extract_skills(resume_text)
    # Case-insensitive matching — preserve original casing in output
    resume_lower = {s.lower(): s for s in resume_skills}
    job_lower    = {s.lower(): s for s in job_skills}
    matched = [resume_lower[s] for s in job_lower if s in resume_lower]
    gaps    = [job_lower[s]    for s in job_lower if s not in resume_lower]
    extra   = [resume_lower[s] for s in resume_lower if s not in job_lower]
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

Return ONLY valid JSON, no markdown fences:
{{
  "summary": "2-3 sentence professional summary mentioning key matched skills",
  "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
  "weaknesses": ["specific weakness 1"],
  "skill_gaps": {json.dumps(gaps[:4]) if gaps else '["No critical gaps"]'},
  "overlapping_skills": {json.dumps(matched)},
  "match_reason": "1-2 sentences explaining the {score:.1f}% score",
  "explanation": "Detailed explanation referencing matched skills"
}}"""

        response = _get_client().chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=900,
        )
        content = re.sub(r'^```(?:json)?\s*', '', response.choices[0].message.content.strip(), flags=re.MULTILINE)
        content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)
        result = json.loads(content)
        result["overlapping_skills"] = matched
        result["skill_gaps"] = gaps[:4] if gaps else ["No critical gaps"]
        return result

    except (json.JSONDecodeError, Exception) as e:
        print(f"Groq error: {e}")
        return _local_insights(job_skills, resume_skills, matched, gaps, extra, score)


def _local_insights(job_skills, resume_skills, matched, gaps, extra, score: float) -> dict:
    n_matched, n_required = len(matched), len(job_skills)
    if score >= 70:
        summary = f"Strong candidate matching {n_matched}/{n_required} required skills" + (f": {', '.join(matched[:3])}." if matched else ".")
    elif score >= 40:
        summary = f"Moderate match with {n_matched}/{n_required} required skills" + (f" including {', '.join(matched[:3])}." if matched else ".") + " Some gaps exist."
    else:
        summary = f"Low match with {n_matched}/{n_required} required skills." + (f" Candidate has: {', '.join(matched[:3])}." if matched else "")

    return {
        "summary": summary,
        "strengths": matched[:4] if matched else ["General domain experience"],
        "weaknesses": [f"Missing required skill: {s}" for s in gaps[:2]] if gaps else ["No major weaknesses detected"],
        "skill_gaps": gaps[:4] if gaps else ["No critical gaps found"],
        "overlapping_skills": matched,
        "match_reason": f"{n_matched} of {n_required} required skills matched" + (f" ({', '.join(matched[:3])})" if matched else "") + f", giving a {score:.1f}% score.",
        "explanation": f"Score: {score:.1f}% — matched {n_matched}/{n_required} required skills." + (f" Matched: {', '.join(matched)}." if matched else "") + (f" Missing: {', '.join(gaps[:3])}." if gaps else ""),
    }
