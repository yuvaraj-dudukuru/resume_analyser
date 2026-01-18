import argparse
import os
import pandas as pd
from src.parser import ResumeParser
from src.scorer import ResumeScorer
from src.email_gen import EmailGenerator
from src.config import load_config
import glob

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
        
        # Score
        score, matches, status = scorer.score(data["raw_text"], jd_text)
        data["score"] = score
        data["matched_keywords"] = matches
        data["status"] = status
        
        # Email
        data["email_draft"] = email_gen.generate(data)
        
        results.append(data)
        
    # Export
    df = pd.DataFrame(results)
    
    # Formatting columns
    cols = ["candidate_name", "email", "phone", "score", "status", "matched_keywords", "email_draft", "raw_text", "filename"]
    # Reorder if columns match
    available_cols = [c for c in cols if c in df.columns]
    df = df[available_cols]
    
    print(f"Writing results to {args.output}...")
    
    # Clean data
    from src.utils import clean_dataframe_for_excel
    df = clean_dataframe_for_excel(df)
    
    with pd.ExcelWriter(args.output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='All Candidates')
        if "status" in df.columns:
            df[df['status'] == 'Green'].to_excel(writer, index=False, sheet_name='Shortlisted')
            df[df['status'] == 'Yellow'].to_excel(writer, index=False, sheet_name='Under Review')
            df[df['status'] == 'Red'].to_excel(writer, index=False, sheet_name='Rejected')

    print("Done!")

if __name__ == "__main__":
    main()
