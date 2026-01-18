import os
import sys

# Add parent directory to path to import existing modules if needed
# But we will likely need to duplicate/refactor some logic if we want to be clean.
# For now, let's assume we can re-use the file reading logic but we want a cleaner interface.

# We will re-implementation simple text extraction wrappers using the libraries directly
# to avoid dependency on the messy resume_parser.py structure, 
# but we will try to respect the original logic where possible.

import pdfminer.high_level
import docx

def extract_text_from_pdf(pdf_path):
    try:
        return pdfminer.high_level.extract_text(pdf_path)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
        return ""

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

class ResumeParser:
    def __init__(self):
        pass

    def parse_file(self, file_path):
        text = extract_text(file_path)
        filename = os.path.basename(file_path)
        
        # simple parsing logic reuse or re-implement
        # We will extract basics
        import re
        
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_pattern = r"\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}"

        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        return {
            "filename": filename,
            "raw_text": text,
            "email": emails[0] if emails else "",
            "phone": phones[0] if phones else "",
            "candidate_name": filename.split(".")[0] # Naive name extraction from filename
        }
