import os
import re
import pdfminer.high_level
import docx

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == ".pdf":
            text = pdfminer.high_level.extract_text(file_path)
        elif ext == ".docx":
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    return text

def extract_candidate_name(text):
    """
    Attempt to extract the candidate's name from the resume text.
    Strategies:
    1. Look for 'Name: <Name>' pattern
    2. Look for the first line that looks like a name (Title Case, no numbers, < 5 words)
    """
    if not text:
        return None

    # Strategy 1: Explicit "Name:" label
    match = re.search(r"Name\s*:\s*([A-Za-z\s]+)", text[:500], re.IGNORECASE)
    if match:
        return match.group(1).strip()
        
    # Strategy 2: First non-empty line that looks like a name
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for i in range(min(10, len(lines))):
        line = lines[i]
        # Heuristics:
        # - 2 to 4 words (First Last, First Middle Last)
        # - Mostly letters
        # - Title Case (roughly)
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(w[0].isupper() for w in words if w[0].isalpha()) and not any(char.isdigit() for char in line):
                 # Avoid common headers like "Curriculum Vitae" or "Resume"
                if "resume" not in line.lower() and "curriculum" not in line.lower() and "profile" not in line.lower():
                    return line
    
    return None

class ResumeParser:
    def __init__(self):
        pass

    def parse_file(self, file_path):
        filename = os.path.basename(file_path)
        text = extract_text(file_path)
        
        if text is None:
            return {
                "filename": filename,
                "error": True,
                "notes": "Failed to extract text (Corrupt/Encrypted)",
                "candidate_name": "Unknown",
                "email": "",
                "phone": "",
                "raw_text": ""
            }

        # simple regex extraction
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_pattern = r"\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}"

        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        extracted_name = extract_candidate_name(text)
        candidate_name = extracted_name if extracted_name else filename.split(".")[0]

        return {
            "filename": filename,
            "raw_text": text,
            "email": emails[0] if emails else "",
            "phone": phones[0] if phones else "",
            "candidate_name": candidate_name,
            "error": False, 
            "notes": ""
        }
