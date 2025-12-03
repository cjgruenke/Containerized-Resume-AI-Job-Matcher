# src/pipeline.py
from pathlib import Path
from typing import Dict, Any, List
import json
from .scraper import JobScraper
from .cleaner import JobCleaner
from .embeddings import IEmbeddingService
from .similarity import SimilarityCalculator
import numpy as np

class Pipeline:
    def __init__(self, scraper: JobScraper, cleaner: JobCleaner, embedder: IEmbeddingService,
                 similarity_calc: SimilarityCalculator):
        self.scraper = scraper
        self.cleaner = cleaner
        self.embedder = embedder
        self.sim_calc = similarity_calc

    def run(self, resume_path: Path = None, top_n: int = 10) -> Dict[str, Any]:
        # Stage 1: fetch
        raw_jobs = self.scraper.fetch()  # list of raw dicts

        # Stage 2: clean
        cleaned_jobs = self.cleaner.clean_jobs(raw_jobs)

        # Stage 2b: resume
        resume_text = ""
        if resume_path and Path(resume_path).exists():
            resume_text = self.cleaner.read_resume(resume_path)
            resume_text = self.cleaner.clean_resume_text(resume_text)
            Path("processed_resume.txt").write_text(resume_text, encoding="utf-8")
        # stage3: embeddings
        job_texts = []
        metas = []
        for j in cleaned_jobs:
            title = j.get("title","")
            company = j.get("companyName","")
            location = j.get("location_normalized") or j.get("location_raw","")
            desc = j.get("description","")
            t = " ".join([p for p in [title, company, location, desc] if p])
            job_texts.append(t)
            metas.append({"job_key": j.get("job_key"), "title": title, "companyName": company, "location": location})

        embeddings = self.embedder.embed_texts(job_texts) if job_texts else []
        jobs_meta_embeddings = []
        for meta, emb in zip(metas, embeddings):
            jobs_meta_embeddings.append({"job_key": meta.get("job_key"), "meta": meta, "embedding": emb})

        # save jobs embeddings to jsonl
        with open("jobs_embeddings.jsonl", "w", encoding="utf-8") as f:
            for r in jobs_meta_embeddings:
                f.write(json.dumps(r) + "\n")

        if resume_text:
            resume_emb = self.embedder.embed_text(resume_text)
            with open("resume_embedding.json", "w", encoding="utf-8") as f:
                json.dump({"model": getattr(self.embedder, "model", "mock"), "embedding": resume_emb}, f, indent=2)
        else:
            resume_emb = None

        # Stage 4: similarity ranking
        if resume_emb:
            top = self.sim_calc.rank(jobs_meta_embeddings, resume_emb, top_n=top_n)
            with open("top_jobs.json", "w", encoding="utf-8") as fo:
                json.dump(top, fo, indent=2)
            # csv summary
            import csv
            with open("top_jobs.csv", "w", encoding="utf-8", newline="") as fcsv:
                writer = csv.DictWriter(fcsv, fieldnames=["rank", "job_key", "title", "company", "location", "similarity"])
                writer.writeheader()
                for i, r in enumerate(top, start=1):
                    writer.writerow({
                        "rank": i,
                        "job_key": r.get("job_key"),
                        "title": r.get("title") or "",
                        "company": r.get("company") or "",
                        "location": r.get("location") or "",
                        "similarity": f"{r.get('similarity'):.6f}"
                    })
        else:
            top = []
        return {"top": top, "jobs_total": len(jobs_meta_embeddings)}
