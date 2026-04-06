import re
from pathlib import Path
from typing import Dict, List
import numpy as np
from PIL import Image
import pytesseract
import easyocr
from docx import Document
import openpyxl
from pptx import Presentation
import fitz
from io import BytesIO
from fastapi import UploadFile
from app.shared.skills import SKILL_ALIASES

reader = easyocr.Reader(['en'], gpu=False)


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\n\r\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills(text: str) -> List[str]:
    normalized = _normalize(text)
    found = []
    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = r'(?<![a-zA-Z])' + re.escape(alias) + r'(?![a-zA-Z])'
            if re.search(pattern, normalized):
                found.append(canonical)
                break
    return list(dict.fromkeys(found))


async def extract_text_from_file(file: UploadFile) -> str:
    if not file or not file.filename:
        return ""
    filename = file.filename.lower()
    ext = Path(filename).suffix
    text = ""
    try:
        await file.seek(0)
        contents = await file.read()
        if ext == '.pdf':
            text = _from_pdf(contents)
        elif ext in ['.doc', '.docx']:
            text = _from_docx(contents)
        elif ext in ['.xls', '.xlsx']:
            text = _from_excel(contents)
        elif ext in ['.ppt', '.pptx']:
            text = _from_pptx(contents)
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            text = _from_image(contents)
        else:
            text = contents.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Extraction error for {filename}: {e}")
        text = ""
    if ext == '.pdf' and len(text.strip()) < 50:
        try:
            await file.seek(0)
            contents = await file.read()
            text = _fallback_ocr(contents)
        except Exception as e:
            print(f"OCR fallback failed: {e}")
    return text.strip()


def parse_resume(text: str) -> Dict:
    skills = extract_skills(text)

    experience = 0
    for pattern in [r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
                    r'(\d+)\s*(?:years?|yrs?)\s*(?:exp|experience)']:
        m = re.search(pattern, text, re.I)
        if m:
            experience = int(m.group(1))
            break

    phone_match = re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text)
    phone = phone_match.group(1).strip() if phone_match else None

    email_match = re.search(r'[\w.\-+]+@[\w\-]+\.[a-zA-Z]{2,}', text)
    email = email_match.group(0) if email_match else None

    name = None
    skip = {"resume", "curriculum", "vitae", "cv", "profile", "summary",
            "objective", "contact", "details", "information"}
    for line in text.splitlines():
        line = line.strip()
        words = line.split()
        if (2 <= len(words) <= 4
                and all(re.match(r"^[a-zA-Z.\-']+$", w) for w in words)
                and not any(w.lower() in skip for w in words)
                and line[0].isupper()):
            name = line
            break

    edu_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "bsc", "msc", "degree"]
    education = next((k.capitalize() for k in edu_keywords if k in text.lower()), "Not Specified")

    return {"skills": skills, "experience_years": experience,
            "education": education, "phone": phone, "email": email, "name": name}


def _from_pdf(contents: bytes) -> str:
    doc = fitz.open(stream=contents, filetype="pdf")
    text = ""
    for page in doc:
        page_text = page.get_text("text")
        if page_text.strip():
            text += page_text
        else:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img) + "\n"
    doc.close()
    return text


def _from_docx(contents: bytes) -> str:
    return "\n".join([p.text for p in Document(BytesIO(contents)).paragraphs])


def _from_excel(contents: bytes) -> str:
    wb = openpyxl.load_workbook(BytesIO(contents), read_only=True)
    text = ""
    for sheet in wb:
        for row in sheet.iter_rows(values_only=True):
            text += " | ".join([str(c) if c is not None else "" for c in row]) + "\n"
    return text


def _from_pptx(contents: bytes) -> str:
    prs = Presentation(BytesIO(contents))
    return "\n".join(shape.text for slide in prs.slides
                     for shape in slide.shapes if hasattr(shape, "text"))


def _from_image(contents: bytes) -> str:
    img = Image.open(BytesIO(contents))
    text = pytesseract.image_to_string(img)
    if len(text.strip()) < 30:
        text = " ".join([r[1] for r in reader.readtext(np.array(img))])
    return text


def _fallback_ocr(contents: bytes) -> str:
    try:
        return pytesseract.image_to_string(Image.open(BytesIO(contents)))
    except Exception:
        return ""
