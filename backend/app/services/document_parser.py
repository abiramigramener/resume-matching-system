# app/services/document_parser.py
import re
from pathlib import Path
from typing import Dict
import numpy as np
from PIL import Image
import pytesseract
import easyocr
from docx import Document
import openpyxl
from pptx import Presentation
import fitz  # PyMuPDF
from io import BytesIO
from fastapi import UploadFile

# Initialize EasyOCR once
reader = easyocr.Reader(['en'], gpu=False)

COMMON_SKILLS = {"python","java","javascript","react","vue","angular","fastapi","django","flask","aws","azure","docker","kubernetes","sql","postgresql","mongodb","machine learning","llm","nlp","ai","data science","devops","git","jenkins","html","css","excel","powerpoint"}

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
            text = extract_from_pdf(contents)
        elif ext in ['.doc', '.docx']:
            text = extract_from_docx(contents)
        elif ext in ['.xls', '.xlsx']:
            text = extract_from_excel(contents)
        elif ext in ['.ppt', '.pptx']:
            text = extract_from_pptx(contents)
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            text = extract_from_image(contents)
        elif ext == '.txt':
            text = contents.decode('utf-8', errors='ignore')
        else:
            text = contents.decode('utf-8', errors='ignore')

    except Exception as e:
        print(f"Extraction error for {filename}: {e}")
        text = ""   # fallback to empty instead of crashing

    # If no text extracted from PDF (scanned), try OCR only if Tesseract is available
    if ext == '.pdf' and len(text.strip()) < 50:
        try:
            await file.seek(0)
            contents = await file.read()
            text = fallback_ocr(contents)
        except Exception as ocr_err:
            print(f"OCR fallback failed: {ocr_err}")
            # Don't crash - return whatever text we have

    return clean_text(text)

def extract_from_pdf(contents: bytes) -> str:
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


def extract_from_docx(contents: bytes) -> str:
    doc = Document(BytesIO(contents))
    return "\n".join([para.text for para in doc.paragraphs])


def extract_from_excel(contents: bytes) -> str:
    wb = openpyxl.load_workbook(BytesIO(contents), read_only=True)
    text = ""
    for sheet in wb:
        for row in sheet.iter_rows(values_only=True):
            text += " | ".join([str(cell) if cell is not None else "" for cell in row]) + "\n"
    return text


def extract_from_pptx(contents: bytes) -> str:
    prs = Presentation(BytesIO(contents))
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text


def extract_from_image(contents: bytes) -> str:
    img = Image.open(BytesIO(contents))
    text = pytesseract.image_to_string(img)
    if len(text.strip()) < 30:
        result = reader.readtext(np.array(img))
        text = " ".join([res[1] for res in result])
    return text


def fallback_ocr(contents: bytes) -> str:
    try:
        img = Image.open(BytesIO(contents))
        return pytesseract.image_to_string(img)
    except:
        return ""


def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def parse_structured_data(text: str) -> Dict:
    skills = [skill for skill in COMMON_SKILLS if skill.lower() in text.lower()]
    
    exp_patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
        r'(\d+)\s*(?:years?|yrs?)\s*(?:exp|experience)'
    ]
    experience = 0
    for pattern in exp_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            experience = int(match.group(1))
            break
    
    edu_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "bsc", "msc", "degree"]
    education = next((kw.capitalize() for kw in edu_keywords if kw in text.lower()), "Not Specified")
    
    return {
        "skills": list(set(skills)),
        "experience_years": experience,
        "education": education,
        "raw_extracted_text": text[:2000]
    }