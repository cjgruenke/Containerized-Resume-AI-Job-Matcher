# AI-Powered Job Matching System

## Overview
This project implements an **AI-powered job-matching system** that:

1. **Scrapes job postings** (using a RapidAPI job scraper).
2. **Cleans and preprocesses** job descriptions.
3. **Embeds** both job postings and a user-supplied resume using:
   - OpenAI Embeddings (`text-embedding-3-small`)  
   OR  
   - A mock embedding service (for offline testing).
4. **Calculates cosine similarity** between the resume embedding and each job posting.
5. Produces the **Top N most similar jobs**, displayed in a clean table.


---

## Project Structure

```
Project2/
│
├── JobMatcher/
│   ├── __init__.py
│   ├── cli.py
│   ├── scraper.py
│   ├── cleaner.py
│   ├── embeddings.py
│   ├── similarity.py
│   ├── pipeline.py
│   ├── utils.py (if applicable)
│   └── ...
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation & Environment Setup (PowerShell)

### 1. Clone the repository
```powershell
git clone https://github.com/cjgruenke/CS325Project2.git
cd CS325Project2
```

### 2. Create a virtual environment
```powershell
python -m venv venv
```

### 3. Activate the virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Set your API keys in PowerShell **each session**, or permanently using `$PROFILE`.

### Temporary (session-only) environment variable
```powershell
$env:RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE"
$env:OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
```

To check:
```powershell
echo $env:RAPIDAPI_KEY
echo $env:OPENAI_API_KEY
```

---

## Running the Application (PowerShell)

### Run with your resume (PDF or TXT)
```powershell
python -m JobMatcher.cli --resume "path\to\resume.pdf"
```

### Run using Mock Embeddings (no API keys required)
```powershell
python -m JobMatcher.cli --use-mock-embedder
```

### Adjust the number of top results
```powershell
python -m JobMatcher.cli --resume resume.pdf --top 15
```

---

## Running the Test Suite

If you have tests inside a `tests/` folder:

### Run with pytest
```powershell
pytest
```

### Run a specific test file
```powershell
pytest tests\test_scraper.py
```

---

## Features Implemented According to Project Guidelines

### Stage 1: Data Acquisition
- Uses a **RapidAPI job search endpoint**.
- Includes:
  - API usage
  - request handling  
  - JSON parsing  
  - error handling

### Stage 2: Data Preprocessing
- Cleaning job descriptions
- Standardizing fields
- Removing HTML tags and noise
- Resume extraction (PDF or plain text)

### Stage 3: Embeddings
- Uses OpenAI embeddings when available.
- Falls back to MockEmbeddingService when:
  - No key provided  
  - OpenAI not installed  

### Stage 4: Similarity + Ranking
- Computes cosine similarity
- Ranks all job postings
- Outputs Top N in a formatted PrettyTable

---

## Docker Usage (Optional)

### Build image
```powershell
docker build -t jobmatcher .
```

### Run container
```powershell
docker run --rm jobmatcher
```