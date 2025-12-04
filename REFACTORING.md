# Refactoring Report — AI-Powered Job Matching Project (Project 2)

## Overview

This document describes the refactoring performed from the original Project 1 code to the current Project 2 implementation. The goal was to improve code maintainability, readability, and adherence to SOLID principles, while keeping the core functionality of scraping job postings, embedding them, embedding a resume, and ranking the top matching jobs.

---

## SOLID Principles Applied

### 1. Single Responsibility Principle (SRP)
**Problem in original code:**  
Each Stage script (Stage1–Stage4) in Project 1 handled multiple responsibilities. For example:
- `Stage1DataAcquisition.py` both handled HTTP requests, response parsing, JSON/CSV writing, and logging.
- `Stage2DataCleaningAndResumeParsing.py` handled both cleaning jobs and parsing resumes.
- `Stage3OpenAIEmbeddings.py` handled file I/O, batching, and embedding API calls in one script.

**Implementation in Project 2:**  
- Introduced modular classes: `JobScraper`, `JobCleaner`, `OpenAIEmbeddingService`, `SimilarityCalculator`, `Pipeline`.
- Each class now has a single, well-defined responsibility:
  - `JobScraper`: only fetches jobs.
  - `JobCleaner`: only cleans job data.
  - `OpenAIEmbeddingService` / `MockEmbeddingService`: only handle embeddings.
  - `SimilarityCalculator`: only calculates similarity.
  - `Pipeline`: orchestrates the flow of these components.

**Before (Stage2 snippet example):**
```python
def preprocess_job_record(raw):
    # cleaned job + resume parsing mixed in one function
    ...
```

**After (Project 2 CLI approach):**
```python
cleaner = JobCleaner()
cleaned_jobs = cleaner.clean(raw_jobs)
resume_embedding = embedder.embed_resume(resume_path)
sim_calc = SimilarityCalculator()
top_jobs = sim_calc.rank(cleaned_jobs, resume_embedding)
```

---

### 2. Dependency Inversion Principle (DIP)
**Problem in original code:**  
- Stage3 directly depended on OpenAI API and `requests`, making testing difficult and tightly coupling the embedding implementation with other logic.
- Stage4 directly handled JSON/CSV I/O along with similarity calculation.

**Implementation in Project 2:**  
- Introduced `IEmbeddingService` interface:
  - `OpenAIEmbeddingService` implements it for real embeddings.
  - `MockEmbeddingService` implements it for testing without hitting the API.
- `Pipeline` and `SimilarityCalculator` depend on the `IEmbeddingService` abstraction rather than a concrete implementation, enabling easy swapping of embeddings.

**Before (Stage3 snippet):**
```python
resp = requests.post(OPENAI_EMBED_URL, headers=HEADERS, json=payload)
embedding = resp.json()["data"][0]["embedding"]
```

**After (Project 2 snippet):**
```python
if use_mock:
    embedder: IEmbeddingService = MockEmbeddingService()
else:
    embedder: IEmbeddingService = OpenAIEmbeddingService(client=openai_client)
resume_vector = embedder.embed_resume(resume_path)
```

---

### 3. Open/Closed Principle (OCP)
**Problem in original code:**  
- Any change in embedding service or similarity metric required editing the Stage3/Stage4 scripts directly.

**Implementation in Project 2:**  
- The design is now open for extension but closed for modification:
  - You can add a new embedding service by implementing `IEmbeddingService`.
  - You can add a new similarity metric by subclassing `SimilarityCalculator` without modifying the existing code.

---

## Benefits Achieved
- Clear separation of concerns.
- Easier testing using `MockEmbeddingService`.
- Pipeline orchestration centralizes execution while leaving individual components focused.
- Extensible to new embedding models or similarity metrics.

---