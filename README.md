# AI-Powered Resume Parser & Scorer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🚀 Overview

The **AI-Powered Resume Parser & Scorer** is a sophisticated tool designed to automate the initial screening process for recruitment. By leveraging traditional NLP techniques and modern Large Language Models (LLMs), it transforms a chaotic folder of resumes into a structured, scored, and categorized dataset.

### ❓ The Problem

High-volume recruitment often involves manually opening hundreds of resumes, Ctrl+F-ing for keywords, and subjectively guessing a candidate's fit. This process is:

- **Time-Consuming**: Hours wasted on irrelevant profiles.
- **Inconsistent**: Different recruiters apply different standards.
- **Prone to Error**: Keyword matching misses implied skills.

### 💡 The Solution

This tool solves these challenges by:

1. **Extracting Data**: Automatically parsing contact info from PDF/DOCX files.
2. **Intelligent Scoring**: Using LLMs (OpenAI/Gemini) to "read" the resume like a human.
3. **Automated Action**: Auto-categorizing candidates and generating personalized email drafts.

---

## ✨ Key Features (v2.0)

- **📄 Advanced Parsing**:
  - Multi-format support (`.pdf`, `.docx`).
  - **Smart Name Extraction**: Uses regex and NLP heuristics to find candidate names, not just filenames.
  - **Robust Error Handling**: Gracefully handles corrupted or encrypted files.
- **🤖 Hybrid Scoring Engine**:
  - **Keyword Mode**: Fast, offline scoring based on weighted skills.
  - **AI Mode**: Uses **OpenAI GPT** or **Google Gemini** for semantic understanding.
  - **Detailed Feedback**: Provides "Matched Keywords" and "Reasoning" for every score.
- **🧹 Smart Processing**:
  - **Duplicate Detection**: Auto-detects duplicate emails and keeps the best resume.
  - **Summary Statistics**: Real-time dashboards of candidate potential.
- **📧 Email Automation**:
  - Generates context-aware email drafts.
  - **Auto-Send**: Optional SMTP integration to send bulk emails directly from the UI.
- **📊 Visual Analytics**:
  - Interactive Pie Charts and Color-coded Data Tables in Streamlit.
  - Excel export with multiple sheets (Summary, Shortlisted, All).

---

## 🚀 Deployment

**Note:** This is a Python application. It **cannot** run on GitHub Pages (which is for static HTML sites). We recommend **Streamlit Community Cloud** (Free).

### Deploy to Streamlit Cloud

1. Push your code to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Click **"New App"**.
4. Select your repository (`resume_analyser`), branch (`main`), and main file (`app.py`).
5. **Secrets**: Click "Advanced Settings" -> "Secrets" and add your keys:

    ```toml
    OPENAI_API_KEY = "sk-..."
    ```

6. Click **Deploy**!

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- (Optional) OpenAI or Google Gemini API Key

### Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yesthisistom/Resume-Parser.git
    cd Resume-Parser
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

---

## 📖 Usage

### Option 1: Web Interface (Recommended)

The Streamlit app provides an intuitive UI for uploading files and visualizing results.

```bash
streamlit run app.py
```

1. Open the URL provided (usually `http://localhost:8501`).
2. **Config**: Enter API Key and Email Settings in the sidebar.
3. **Input**: Paste Job Description and Upload Resumes.
4. **Analyze**: Click "Process Resumes". View dynamic charts and color-coded table.
5. **Act**: Download Excel or click "Send Emails".

### Option 2: Command Line Interface (CLI)

For batch processing large datasets.

**With AI Scoring:**

```bash
# Windows
set OPENAI_API_KEY=sk-your-key-here
python main.py -i "./resumes" -j "job_description.txt"
```

---

## ⚙️ Configuration

The system behavior is controlled by `config.yaml`.

```yaml
scoring:
  red_threshold: 40    # Scores below this are Rejected
  green_threshold: 70  # Scores above this are Interviewed
  bonus_weights:       
    python: 1.5

llm:
  provider: "openai"   # Auto-detected based on key
  model: "gpt-3.5-turbo"

email_templates:
  green: |
    Subject: Interview Invitation
    Dear {candidate_name}, ...
```

## 📂 Project Structure

```text
resume-parser/
├── app.py              # Streamlit Web Application
├── main.py             # CLI Entry
├── src/
│   ├── parser.py       # Regex & PDFMiner Logic
│   ├── scorer.py       # Hybrid Scoring Engine
│   ├── email_gen.py    # Template Engine
│   ├── utils.py        # Stats, Duplicates, Cleaning
└── ...
```

## 🤝 Contributing

Contributions are welcome!

## 📄 License

Distributed under the MIT License.
