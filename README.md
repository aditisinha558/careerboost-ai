
# CareerBoost AI 

This is an portfolio-ready CareerBoost AI with the following features:
- Upload Resume (PDF) or paste plain text.
- Paste Job Description.
- ATS keyword match and match-rate score (keyword match & skill gap).
- Score breakdown: Keyword Match Score, Readability Score (simple proxy), Overall Score.
- Action-verb suggestions and rule-based resume rewriting (weak→strong verbs).
- AI-like tailored cover-letter generator (template-based using matched keywords).
- Visual charts: bar chart for score breakdown and word-cloud for job keywords.
- Downloadable PDF reports (analysis) and an "optimized resume" text file.
- Streamlit UI for quick deployment on Streamlit Cloud or for local demo in PyCharm.

## Installation (local)
1. Create & activate a Python virtual environment (Python 3.8+):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords
```

3. Run locally:
```bash
streamlit run app.py
```

Open the displayed local URL (usually http://localhost:8501) in your browser.

Notes:
- The app uses spaCy when available; otherwise it falls back to simple tokenization.
- This starter avoids using any paid APIs. You can later integrate GPT APIs for advanced rewriting/suggestions.
- Designed to be edited in PyCharm Community Edition (no paid plugins required).
