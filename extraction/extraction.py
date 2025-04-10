import os
import subprocess
import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
from langdetect import detect

# Supported OCR languages
LANGUAGES = (
    "eng+mar+hin+tam+tel+guj+kan+ben+ori+pan+fra+spa+deu+chi_sim+jpn+rus+ara"
)

def extract_text_from_pdf(pdf_path, lang=LANGUAGES):
    try:
        doc = fitz.open(pdf_path)
        texts = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                texts.append(text)
            else:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr = pytesseract.image_to_string(img, lang=lang)
                texts.append(ocr)
        return "\n".join(texts)
    except Exception as e:
        print(f"[extract_pdf] Error: {e}")
        return ""


def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"[extract_docx] Error: {e}")
        return ""


def extract_text_from_doc(path):
    try:
        res = subprocess.run(["catdoc", path], capture_output=True, text=True)
        return res.stdout
    except Exception as e:
        print(f"[extract_doc] Error: {e}")
        return ""


def extract_text_from_txt(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[extract_txt] Error: {e}")
        return ""


def extract_text_from_image(path, lang=LANGUAGES):
    try:
        img = Image.open(path)
        return pytesseract.image_to_string(img, lang=lang)
    except Exception as e:
        print(f"[extract_img] Error: {e}")
        return ""


def detect_language(text):
    try:
        clean = " ".join(text.split())
        return detect(clean) if len(clean) > 10 else "unknown"
    except:
        return "unknown"


def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".docx":
        return extract_text_from_docx(path)
    if ext == ".doc":
        return extract_text_from_doc(path)
    if ext == ".txt":
        return extract_text_from_txt(path)
    if ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        return extract_text_from_image(path)
    print(f"Unsupported format: {ext}")
    return ""