# Resume Parser & Scorer AI

This tool parses resumes (PDF, DOCX) from a directory, scores them against a Job Description, and categorizes them into **Red/Yellow/Green** buckets. It also generates email drafts for each candidate.

## Features

- **Parsing**: Extracts name, email, phone, and text from PDF/DOCX.
- **Scoring**: Keywords-based scoring against JD with configurable weights.
- **Categorization**: Auto-assigns status based on score thresholds.
- **Email Generation**: Creates personalized email drafts based on status.
- **Interfaces**:
  - **Streamlit Web UI**: Easy to use drag-and-drop interface.
  - **CLI**: Batch processing for power users.

## AI / LLM Support (New!)

To use **OpenAI (ChatGPT)** or **Google Gemini** for "smart" scoring:

1. Get your API Key.
2. Enter it in the **Web UI sidebar**.
3. OR set it as an environment variable for CLI: `set OPENAI_API_KEY=sk-...`

If no API key is provided, it falls back to **Keyword Matching**.

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Interface (Recommended)

Run the Streamlit app:

```bash
streamlit run app.py
```

This will open a browser window where you can upload resumes and paste your JD.

### Command Line Interface

Run the script pointing to your resume folder:

```bash
python main.py -i "path/to/resumes" -j "job_description.txt" -o "results.xlsx"
```

## Configuration

Edit `config.yaml` to change:

- Scoring thresholds (`red_threshold`, `green_threshold`)
- Bonus skill weights
- Email templates

## Docker (Optional)

(Optional instructions if you want to containerize)
