
import re
import fitz  # PyMuPDF
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

WEAK_TO_STRONG = {
    "helped": "collaborated with/assisted in",
    "did": "executed/implemented",
    "worked": "contributed/implemented",
    "managed": "led/supervised",
    "responsible": "owned/oversaw",
    "handled": "coordinated/managed",
    "used": "utilized/leveraged",
    "made": "developed/engineered",
    "improved": "optimized/enhanced"
}

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text") + "\\n"
    return text

def simple_tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\\s]', ' ', text)
    tokens = [t.strip() for t in text.split() if t.strip()]
    return tokens

def extract_keywords(text):
    if nlp is not None:
        doc = nlp(text.lower())
        kws = {token.lemma_ for token in doc if token.is_alpha and not token.is_stop}
        return kws
    else:
        return set(simple_tokenize(text))

def match_keywords(resume_text, job_text):
    resume_kw = extract_keywords(resume_text)
    job_kw = extract_keywords(job_text)
    matched = sorted(list(resume_kw & job_kw))
    missing = sorted(list(job_kw - resume_kw))
    keyword_score = int((len(matched) / max(1, len(job_kw))) * 100)
    return keyword_score, matched, missing

def suggest_action_words(text):
    suggestions = {}
    if nlp is not None:
        doc = nlp(text)
        for token in doc:
            if token.pos_ == "VERB":
                w = token.text.lower()
                if w in WEAK_TO_STRONG:
                    suggestions[w] = WEAK_TO_STRONG[w]
    else:
        tokens = simple_tokenize(text)
        for w in tokens:
            if w in WEAK_TO_STRONG:
                suggestions[w] = WEAK_TO_STRONG[w]
    return suggestions

def readability_score(text):
    # Simple proxy for readability: shorter sentences + moderate word length -> better.
    sentences = re.split(r'[\\.\\n\\?!]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = simple_tokenize(text)
    if not sentences or not words:
        return 50
    avg_words_per_sentence = len(words) / max(1, len(sentences))
    avg_word_length = sum(len(w) for w in words) / max(1, len(words))
    # Heuristic mapping to 0-100 (lower avg words per sentence and moderate word length -> higher score)
    score = 100 - (avg_words_per_sentence * 3) - (avg_word_length * 2)
    score = max(10, min(95, int(score)))
    return score

def overall_score(keyword_score, readability):
    # weighted average: keywords 70%, readability 30%
    return int((keyword_score * 0.7) + (readability * 0.3))

def rewrite_resume_text(resume_text, matched_keywords, missing_keywords):
    # Simple rule-based rewrite:
    # 1. Replace weak verbs with stronger phrases
    # 2. Add a suggested 'Skills to add' section at top for missing keywords
    lines = resume_text.splitlines()
    rewritten = []
    for line in lines:
        new_line = line
        for w, s in WEAK_TO_STRONG.items():
            pattern = r'\\b' + re.escape(w) + r'\\b'
            new_line = re.sub(pattern, s, new_line, flags=re.IGNORECASE)
        rewritten.append(new_line)
    skills_section = ""
    if missing_keywords:
        skills_section = "Suggested skills to add: " + ", ".join(missing_keywords[:12]) + "\\n\\n"
    return skills_section + "\\n".join(rewritten)
