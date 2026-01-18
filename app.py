import streamlit as st
import os
import pandas as pd
from src.parser import ResumeParser
from src.scorer import ResumeScorer
from src.email_gen import EmailGenerator
from src.config import load_config
import tempfile
import shutil

# Page Config
st.set_page_config(page_title="Resume Parser & Scorer", page_icon="📄", layout="wide")

st.title("📄 Resume Parser & Scorer AI")
st.markdown("Upload resumes, score them against your JD, and get automated email drafts.")

# Sidebar Config
st.sidebar.header("Configuration")
config = load_config()

# API Key Input
api_key = st.sidebar.text_input("OpenAI/Gemini API Key (Optional)", type="password", help="Leave empty to use Basic Keyword Matching")

# Load modules
parser_module = ResumeParser()
# Pass API Key to Scorer
scorer_module = ResumeScorer(config, api_key=api_key if api_key else None)
email_module = EmailGenerator(config)

# Input: Job Description
st.subheader("1. Job Description")
default_jd = "Python, Django, React, REST API, SQL, 5+ years experience"
job_description = st.text_area("Paste the Job Description or Keywords here:", value=default_jd, height=150)

# Input: Resumes
st.subheader("2. Upload Resumes")
uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

if st.button("Process Resumes"):
    if not uploaded_files:
        st.error("Please upload at least one resume.")
    elif not job_description:
        st.error("Please provide a Job Description.")
    else:
        results = []
        progress_bar = st.progress(0)
        
        # Create a temp dir to save uploaded files for processing (parser expects paths)
        with tempfile.TemporaryDirectory() as temp_dir:
            for idx, uploaded_file in enumerate(uploaded_files):
                # Save file
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse
                parsed_data = parser_module.parse_file(file_path)
                
                # Score
                score, matches, status = scorer_module.score(parsed_data["raw_text"], job_description)
                parsed_data["score"] = score
                parsed_data["matched_keywords"] = matches
                parsed_data["status"] = status
                
                # Email
                email_body = email_module.generate(parsed_data)
                parsed_data["email_draft"] = email_body
                
                results.append(parsed_data)
                progress_bar.progress((idx + 1) / len(uploaded_files))
        
        st.success(f"Processed {len(results)} resumes!")
        
        # Display Results
        df = pd.DataFrame(results)
        
        # Reorder columns for display
        display_cols = ["candidate_name", "email", "score", "status", "matched_keywords"]
        st.dataframe(df[display_cols].style.applymap(
            lambda x: "background-color: #ffcccc" if x == "Red" else ("background-color: #ffffcc" if x == "Yellow" else "background-color: #ccffcc"),
            subset=["status"]
        ))
        
        # Export
        st.subheader("3. Export Results")
        
        # Clean data for Excel
        from src.utils import clean_dataframe_for_excel
        df = clean_dataframe_for_excel(df)
        
        # Create Excel in memory
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='All Candidates')
            
            # Separate sheets?
            df[df['status'] == 'Green'].to_excel(writer, index=False, sheet_name='Shortlisted')
        
        st.download_button(
            label="Download Excel Report",
            data=output.getvalue(),
            file_name="resume_scoring_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Detailed View
        st.subheader("Detailed Review")
        for i, row in df.iterrows():
            with st.expander(f"{row['candidate_name']} - {row['status']} ({row['score']:.1f})"):
                st.write(f"**Email:** {row['email']}")
                st.write(f"**Phone:** {row['phone']}")
                st.write(f"**Matches:** {row['matched_keywords']}")
                st.text_area("Email Draft", row['email_draft'], height=200)

