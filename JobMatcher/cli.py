# JobMatcher/cli.py

import argparse
import os
from pathlib import Path
from .scraper import JobScraper
from .cleaner import JobCleaner
from .embeddings import OpenAIEmbeddingService, MockEmbeddingService, IEmbeddingService
from .similarity import SimilarityCalculator
from .pipeline import Pipeline
from prettytable import PrettyTable

try:
    import openai
except ImportError:
    openai = None


def parse_args():
    parser = argparse.ArgumentParser(description="Job Matcher CLI")
    parser.add_argument("--resume", type=str, default=None, help="Path to resume PDF or TXT")
    parser.add_argument("--use-mock-embedder", action="store_true", help="Use MockEmbeddingService for testing")
    parser.add_argument("--top", type=int, default=10, help="Number of top results to display")
    return parser.parse_args()


def truncate_text(text: str, max_len=40) -> str:
    """Truncate text with ellipsis if too long."""
    if not text:
        return "N/A"
    text = text.replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len-3] + "..."


def normalize_location(loc: str, max_len=40) -> str:
    """Clean up verbose location strings to a uniform 'City, ST' style."""
    if not loc:
        return "N/A"
    loc = loc.replace("\n", " ").strip()

    # Attempt to parse verbose API output with city/state keywords
    if "city" in loc.lower():
        parts = []
        for segment in loc.split(","):
            segment = segment.strip()
            # extract value after keyword
            if segment.lower().startswith("city") or segment.lower().startswith("state") or segment.lower().startswith("postalcode"):
                if " " in segment:
                    parts.append(segment.split(" ", 1)[1])
            else:
                parts.append(segment)
        loc = ", ".join(parts[:2])  # just city and state
    # truncate if still too long
    return loc if len(loc) <= max_len else loc[:max_len-3] + "..."


def main():
    args = parse_args()

    # --- Scraper configuration ---
    payload = {
        "scraper": {
            "maxRows": 15,
            "query": "Developer",
            "location": "Saint Louis MO",
            "jobType": "fulltime",
            "radius": "50",
            "sort": "relevance",
            "fromDays": "7",
            "country": "us"
        }
    }
    rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
    host = "indeed-scraper-api.p.rapidapi.com"
    scraper = JobScraper(api_key=rapidapi_key, host=host, payload=payload)

    # --- Cleaner ---
    cleaner = JobCleaner()

    # --- Embedding Service ---
    if args.use_mock_embedder or (openai is None):
        embedder: IEmbeddingService = MockEmbeddingService()
    else:
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if not openai_key:
            print("No OpenAI API key found. Falling back to MockEmbeddingService.")
            embedder = MockEmbeddingService()
        else:
            client = openai.OpenAI(api_key=openai_key)
            embedder = OpenAIEmbeddingService(client=client)

    # --- Similarity Calculator ---
    sim_calc = SimilarityCalculator()

    # --- Pipeline ---
    pipeline = Pipeline(scraper, cleaner, embedder, sim_calc)

    # --- Run pipeline ---
    resume_path = Path(args.resume) if args.resume else None
    result = pipeline.run(resume_path=resume_path, top_n=args.top)

    top_results = result.get("top", [])
    jobs_total = result.get("jobs_total", 0)

    if not top_results:
        print("No results found.")
        return

    # --- PrettyTable output ---
    table = PrettyTable()
    table.field_names = ["Rank", "Title", "Company", "Location", "Score"]

    for idx, job in enumerate(top_results, 1):
        meta = job.get("meta", {})
        table.add_row([
            idx,
            truncate_text(meta.get("title")),
            truncate_text(meta.get("companyName")),
            normalize_location(meta.get("location")),
            f"{job.get('similarity', 0):.4f}"
        ])

    print("\n==== TOP MATCHING JOBS ====\n")
    print(table)
    print(f"\nFound {len(top_results)} matching results out of {jobs_total} total.\n")


if __name__ == "__main__":
    main()
