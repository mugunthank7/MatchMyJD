# 🚀 MatchMyJD – AI-Powered Resume–Job Description Matching Engine

**MatchMyJD** is an intelligent job–resume matching system designed to evaluate how well a candidate fits a job description using:

* JD preprocessing and noise removal
* LLM-based JD and resume analysis (Gemini)
* Hybrid matching engine
* Skill normalization and synonym mapping
* Exact, fuzzy, and semantic matching pipelines

It produces transparent, ATS-style scoring across hard skills, soft skills, tools/frameworks, and domains, along with a final match percentage.

---

## ✨ Core Features

### 1. Job Description Analyzer

* Cleans raw JD text from websites.
* Extracts structured fields:

  * Hard skills
  * Soft skills
  * Tools & frameworks
  * Role title + seniority
  * Domains & responsibilities
* Uses Gemini Flash for structured extraction.

### 2. Resume Analyzer

* Extracts structured resume data from PDFs:

  * Skills
  * Experience
  * Projects
  * Education
  * Domains
* Uses PyMuPDF for parsing.
* Sends curated resume sections to Gemini for interpretation.

### 3. Hybrid Matching Engine

The final score is computed using three similarity layers:

| Layer    | Method                 | Purpose                        |
| -------- | ---------------------- | ------------------------------ |
| Exact    | Direct string match    | High precision                 |
| Fuzzy    | Token-based Jaccard    | Handles phrasing variations    |
| Semantic | LLM similarity scoring | Understands conceptual meaning |

Each category (hard/soft/tools/domains) has its own weight, contributing to the overall match score.

### 4. Skill Normalization

* Converts noisy text into canonical skill forms
* Synonym mapping: ML → Machine Learning, NN → Deep Learning, etc.
* Stopword cleaning

---

## 🏗️ Project Structure

```
MatchMyJD/
│
├── config/
│   └── settings.py
│
├── core/
│   ├── jd_preprocessor.py
│   ├── jd_analyzer.py
│   ├── resume_parser.py
│   └── resume_analyzer.py
│
├── matching/
│   ├── matcher_exact.py
│   ├── matcher_fuzzy.py
│   ├── matcher_semantic.py
│   └── hybrid_scorer.py
│
├── utils/
│   ├── json_extractor.py
│   └── logger.py
│
├── ui/
│   └── app.py
│
├── data/samples/
├── run_match.py
└── README.md
```

---

## 🔐 Environment Setup

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Create `.env`

```
GEMINI_API_KEY=your_api_key_here
```

---

## ▶️ Run the Pipeline

```
python3 -m run_match
```

This will:

1. Analyze sample resume
2. Analyze sample JD
3. Run hybrid matching
4. Output final score + detailed breakdown

---

## 📊 Output Example

```
==============================
📌 FINAL MATCH RESULT
==============================

Overall Score: 78.4%

Hard Skills:
  Matched: ML, Python, Data Structures
  Missing: Regression, Time Series

Tools:
  Matched: Git, Docker, NumPy, Spark
  Missing: Java, R

Soft Skills:
  Matched: Communication, Collaboration
  Missing: Proactiveness

Domains:
  Matched: Data Science
  Missing: Predictive Maintenance
```

---

## 🚧 Future Enhancements

* Improved JD parsing to avoid LLM over-expansion
* Ontology-based skill clustering (ML → AI → CS)
* Replace semantic LLM calls with embedding similarity
* Add a Streamlit UI for uploads
* Better score calibration to match ATS systems

---

## 💡 Why This Project Exists

Job descriptions and resumes rarely use identical phrasing. ATS systems often reject strong candidates. MatchMyJD fixes this using:

* Semantic understanding
* Transparent scoring
* Fully modular, developer-friendly architecture

---

If you want badges, screenshots, or a logo for this repo, I can add them.
