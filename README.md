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
- **Prone to Error**: Keyword matching misses implied skills (e.g., "built a REST API" implies "Backend Development").

### 💡 The Solution

This tool solves these challenges by:

1. **Extracting Data**: Automatically parsing contact info, experience, and raw text from PDF/DOCX files.
2. **Intelligent Scoring**: Using LLMs (OpenAI/Gemini) to "read" the resume like a human and score it against the Job Description.
3. **Automated Action**: Auto-categorizing candidates (Red/Yellow/Green) and generating personalized email drafts for each.

---

## ✨ Key Features

- **📄 Multi-Format Support**: Robust parsing for `.pdf` and `.docx` formats.
- **🤖 Hybrid Scoring Engine**:
  - **Keyword Mode**: Fast, offline scoring based on weighted skills.
  - **AI Mode**: Uses **OpenAI GPT** or **Google Gemini** for semantic understanding and reasoning.
- **📊 Smart Categorization**: Automatically buckets candidates into *Green (Interview)*, *Yellow (Review)*, and *Red (Reject)*.
- **📧 Email Automation**: Generates context-aware email drafts ready for sending.
- **🖥️ Dual Interfaces**:
  - **Web UI (Streamlit)**: Modern, drag-and-drop interface for recruiters.
  - **CLI**: Powerful command-line tool for developers and batch processing.

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- (Optional) OpenAI or Google Gemini API Key for AI features

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
2. Enter your **Job Description** (text).
3. Upload **Resume Files** (PDF/DOCX).
4. (Optional) Enter your **API Key** in the sidebar for AI Scoring.
5. Click **Process Resumes** and download the Excel report.

### Option 2: Command Line Interface (CLI)

For integrating into pipelines or processing large batches without a UI.

**Basic Usage:**

```bash
python main.py -i "./resumes" -j "job_description.txt" -o "report.xlsx"
```

**With AI Scoring:**
Set your API key as an environment variable before running:

```bash
# Windows
set OPENAI_API_KEY=sk-your-key-here
python main.py -i "./resumes" -j "job_description.txt"

# Linux/Mac
export GEMINI_API_KEY=AIza-your-key-here
python main.py -i "./resumes" -j "job_description.txt"
```

---

## ⚙️ Configuration

The system behavior is controlled by `config.yaml`. You can customize thresholds, weights, and templates.

```yaml
scoring:
  red_threshold: 40    # Scores below this are Rejected
  green_threshold: 70  # Scores above this are Interviewed
  bonus_weights:       # Multipliers for critical skills
    python: 1.5
    java: 1.2

llm:
  provider: "openai"   # Default provider (auto-overridden by API key detection)
  model: "gpt-3.5-turbo"

email_templates:
  green: |
    Subject: Interview Invitation
    Dear {candidate_name}, ...
```

---

## 📂 Project Structure

```text
resume-parser/
├── app.py              # Streamlit Web Application entry point
├── main.py             # CLI entry point
├── config.yaml         # Configuration file
├── requirements.txt    # Python dependencies
├── src/
│   ├── parser.py       # wrapper for pdfminer/python-docx
│   ├── scorer.py       # specific scoring logic (Keyword + LLM)
│   ├── email_gen.py    # template engine for emails
│   ├── utils.py        # helpers (text sanitation, etc.)
│   └── config.py       # config loader
└── README.md           # Documentation
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
