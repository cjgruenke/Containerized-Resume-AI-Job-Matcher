# tests/test_pipeline_integration.py
from JobMatcher.scraper import JobScraper
from JobMatcher.cleaner import JobCleaner
from JobMatcher.embeddings import MockEmbeddingService
from JobMatcher.similarity import SimilarityCalculator
from JobMatcher.pipeline import Pipeline
from pathlib import Path
import json

def test_pipeline_handles_empty_jobs(tmp_path, monkeypatch):
    # make a scraper that returns empty list
    class DummyScraper:
        def fetch(self):
            return []

    scraper = DummyScraper()
    cleaner = JobCleaner()
    embedder = MockEmbeddingService()
    sim = SimilarityCalculator()
    pipeline = Pipeline(scraper, cleaner, embedder, sim)
    result = pipeline.run(resume_path=None, top_n=5)
    assert result["jobs_total"] == 0
    assert result["top"] == []
