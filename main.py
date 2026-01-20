import argparse
import os
import pandas as pd
from datetime import datetime
import glob
from src.parser import ResumeParser
from src.scorer import ResumeScorer
from src.email_gen import EmailGenerator
from src.config import load_config
from src.utils import clean_dataframe_for_excel, detect_duplicates, generate_summary_stats

def main():
    parser = argparse.ArgumentParser(description="Resume Parser & Scorer CLI")
    parser.add_argument("-i", "--input", required=True, help="Input directory containing resumes")
    parser.add_argument("-j", "--job_description", required=True, help="Job description text file or string")
    parser.add_argument("-o", "--output", default="output.xlsx", help="Output Excel file path")
    
    args = parser.parse_args()
    
    # Load Config
    config = load_config()
    
    # Initialize Modules
    resume_parser = ResumeParser()
    
    # Check for API Key in Env
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        print("Using LLM for scoring (API Key found)")
    else:
        print("Using Basic Keyword Scoring (No API Key found)")
        
    scorer = ResumeScorer(config, api_key=api_key)
    email_gen = EmailGenerator(config)
    
    # Get JD
    if os.path.isfile(args.job_description):
        with open(args.job_description, "r", encoding="utf-8") as f:
            jd_text = f.read()
    else:
        jd_text = args.job_description
        
    # Get Files
    files = glob.glob(os.path.join(args.input, "*.*"))
    supported_exts = [".pdf", ".docx", ".txt"]
    files = [f for f in files if os.path.splitext(f)[1].lower() in supported_exts]
    
    if not files:
        print(f"No supported files found in {args.input}")
        return

    print(f"Found {len(files)} resumes. Processing...")
    
    results = []
    
    for idx, file_path in enumerate(files):
        print(f"[{idx+1}/{len(files)}] Processing {os.path.basename(file_path)}...")
        
        # Parse
        data = resume_parser.parse_file(file_path)
        
        # Score (only if valid)
        if not data.get("error"):
            score, notes, status, matches = scorer.score(data["raw_text"], jd_text)
            data["score"] = score
            data["reasoning"] = notes
            data["status"] = status
            data["matched_keywords"] = matches
        else:
            data["score"] = 0
            data["reasoning"] = data.get("notes", "Error")
            data["status"] = "Error"
            data["matched_keywords"] = ""
        
        # Email
        data["email_draft"] = email_gen.generate(data)
        
        results.append(data)
        
    # DataFrame Logic
    df = pd.DataFrame(results)
    
    # 1. Duplicate Detection
    df = detect_duplicates(df)
    
    # 2. Summary Stats
    stats = generate_summary_stats(df)
    
    print("\n--- Summary ---")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print("----------------")
    
    # Formatting columns
    cols = ["candidate_name", "email", "phone", "score", "status", "reasoning", "matched_keywords", "email_draft", "notes", "filename"]
    # Reorder if columns match
    available_cols = [c for c in cols if c in df.columns]
    df = df[available_cols]
    
    # Clean for Export
    df = clean_dataframe_for_excel(df)
    
    print(f"Writing results to {args.output}...")
    with pd.ExcelWriter(args.output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='All Candidates')
        
        # Summary Sheet
        pd.DataFrame([stats]).to_excel(writer, index=False, sheet_name='Summary')
        
        if "status" in df.columns:
            if 'Green' in df['status'].values:
                df[df['status'] == 'Green'].to_excel(writer, index=False, sheet_name='Shortlisted')
            if 'Yellow' in df['status'].values:
                df[df['status'] == 'Yellow'].to_excel(writer, index=False, sheet_name='Under Review')
            if 'Red' in df['status'].values:
                df[df['status'] == 'Red'].to_excel(writer, index=False, sheet_name='Rejected')

    print("Done!")

if __name__ == "__main__":
    main()
