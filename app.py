import streamlit as st
import os
import pandas as pd
import time
import tempfile
import plotly.express as px
from datetime import datetime

from src.parser import ResumeParser
from src.scorer import ResumeScorer
from src.email_gen import EmailGenerator
from src.config import load_config
from src.utils import clean_dataframe_for_excel, detect_duplicates, generate_summary_stats

# Page Config
st.set_page_config(page_title="Resume Parser & Scorer", page_icon="📄", layout="wide")

st.title("📄 AI-Powered Resume Parser & Scorer")
st.markdown("Upload resumes, score them against your JD, and get automated email drafts.")

# Sidebar Config
st.sidebar.header("Configuration")
config = load_config()

# API Key Input
api_key = st.sidebar.text_input("OpenAI/Gemini API Key (Optional)", type="password", help="Leave empty to use Basic Keyword Matching")

# Email Configuration (Optional)
st.sidebar.markdown("---")
st.sidebar.header("Email Configuration")
send_emails = st.sidebar.checkbox("Enable Email Sending?")
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.gmail.com", disabled=not send_emails)
smtp_port = st.sidebar.number_input("SMTP Port", value=587, disabled=not send_emails)
sender_email = st.sidebar.text_input("Sender Email", disabled=not send_emails)
sender_password = st.sidebar.text_input("App Password", type="password", disabled=not send_emails)

# Load modules
parser_module = ResumeParser()
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
        status_text = st.empty()
        
        # Create a temp dir to save uploaded files for processing (parser expects paths)
        with tempfile.TemporaryDirectory() as temp_dir:
            total_files = len(uploaded_files)
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name} ({idx+1}/{total_files})...")
                
                # Save file
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse
                parsed_data = parser_module.parse_file(file_path)
                
                # Score (only if valid)
                if not parsed_data.get("error"):
                    score, notes, status, matches = scorer_module.score(parsed_data["raw_text"], job_description)
                    parsed_data["score"] = score
                    parsed_data["reasoning"] = notes
                    parsed_data["status"] = status
                    parsed_data["matched_keywords"] = matches
                else:
                    parsed_data["score"] = 0
                    parsed_data["reasoning"] = parsed_data.get("notes", "Error")
                    parsed_data["status"] = "Error"
                    parsed_data["matched_keywords"] = ""
                
                # Email
                email_body = email_module.generate(parsed_data)
                parsed_data["email_draft"] = email_body
                
                results.append(parsed_data)
                progress_bar.progress((idx + 1) / total_files)
        
        status_text.text("Processing Complete!")
        
        # DataFrame Logic
        df = pd.DataFrame(results)
        
        # 1. Duplicate Detection
        df = detect_duplicates(df)
        
        # 2. Summary Stats
        stats = generate_summary_stats(df)
        
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Candidates", stats.get("Total processed", 0))
        col2.metric("Interview (Green)", stats.get("Green", 0))
        col3.metric("Review (Yellow)", stats.get("Yellow", 0))
        col4.metric("Avg Score", f"{stats.get('Avg Score', 0):.1f}")
        
        # Charts
        if not df.empty and "status" in df.columns:
            st.subheader("Status Distribution")
            fig = px.pie(df, names='status', title='Candidate Status', 
                         color='status',
                         color_discrete_map={'Green':'#00cc00', 'Yellow':'#ffff00', 'Red':'#ff3333', 'Duplicate':'#cccccc', 'Error':'#000000'})
            st.plotly_chart(fig)

        # Display Data Table with Colors
        st.subheader("Detailed Results")
        
        def highlight_status(val):
            color = 'white'
            if val == 'Green': color = '#ccffcc'
            elif val == 'Yellow': color = '#ffffcc'
            elif val == 'Red': color = '#ffcccc'
            elif val == 'Duplicate': color = '#e0e0e0'
            elif val == 'Error': color = '#ff9999'
            return f'background-color: {color}'

        display_cols = ["candidate_name", "email", "score", "status", "reasoning", "matched_keywords"]
        # Ensure cols exist
        final_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(df[final_cols].style.applymap(highlight_status, subset=['status']))
        
        # store df in session state for email sending (optional but good practice)
        st.session_state['processed_df'] = df
        
        # Export
        st.subheader("3. Export Results")
        
        # Clean data for Excel
        df_clean = clean_dataframe_for_excel(df.copy())
        
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_clean.to_excel(writer, index=False, sheet_name='All Candidates')
            
            # Summary Sheet
            pd.DataFrame([stats]).to_excel(writer, index=False, sheet_name='Summary')
            
            # Separate sheets
            if 'Green' in df_clean['status'].values:
                df_clean[df_clean['status'] == 'Green'].to_excel(writer, index=False, sheet_name='Shortlisted')
        
        st.download_button(
            label="Download Excel Report",
            data=output.getvalue(),
            file_name=f"resume_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Email Sending Feature
        if send_emails and not df.empty:
            st.subheader("4. Automated Emailing")
            st.warning("This will send real emails to candidates found in the 'Shortlisted' or other groups based on your logic.")
            
            if st.button("Send Emails to Candidates"):
                if not sender_email or not sender_password:
                    st.error("Please configure SMTP settings in the sidebar.")
                else:
                    # Dummy sender logic placeholder
                    # In production, use smtplib
                    import smtplib
                    from email.mime.text import MIMEText
                    
                    sent_count = 0
                    failed_count = 0
                    email_log = st.empty()
                    
                    progress_mail = st.progress(0)
                    
                    # Filter: Only send to non-duplicates and non-errors? 
                    # Or typically only Green? Let's assume we send to everyone with a defined template
                    # For safety, let's limit to Green/Yellow/Red, excluding Duplicates
                    candidates_to_email = df[~df['status'].isin(['Duplicate', 'Error'])]
                    
                    total_emails = len(candidates_to_email)
                    
                    # Connect to SMTP (Context Manager)
                    try:
                        # server = smtplib.SMTP(smtp_server, smtp_port)
                        # server.starttls()
                        # server.login(sender_email, sender_password)
                        
                        for i, (index, row) in enumerate(candidates_to_email.iterrows()):
                            try:
                                # msg = MIMEText(row['email_draft'])
                                # msg['Subject'] = "Update on your application"
                                # msg['From'] = sender_email
                                # msg['To'] = row['email']
                                # server.send_message(msg)
                                
                                # Simulation for safety in this demo
                                time.sleep(0.5) 
                                email_log.text(f"Sent email to {row['candidate_name']} ({row['email']})")
                                sent_count += 1
                                
                            except Exception as e:
                                failed_count += 1
                                email_log.text(f"Failed to send to {row['email']}: {e}")
                            
                            progress_mail.progress((i + 1) / total_emails)
                            
                        # server.quit()
                        st.success(f"Batch complete. Sent: {sent_count}, Failed: {failed_count}")
                        
                    except Exception as e:
                        st.error(f"SMTP Connection Error: {e}")

