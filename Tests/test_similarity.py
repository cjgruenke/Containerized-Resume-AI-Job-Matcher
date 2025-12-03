# tests/test_similarity.py
from JobMatcher.similarity import SimilarityCalculator
from JobMatcher.embeddings import MockEmbeddingService

def test_rank_orders_similar_first():
    mock = MockEmbeddingService(dim=4)
    # create three fake job texts
    texts = ["python developer", "accountant", "senior python dev"]
    embs = mock.embed_texts(texts)
    jobs = []
    for i, t in enumerate(texts):
        jobs.append({"job_key": f"j{i}", "meta": {"title": t, "companyName": "X"}, "embedding": embs[i]})
    resume = mock.embed_text("senior python developer")
    sim = SimilarityCalculator()
    top = sim.rank(jobs, resume, top_n=3)
    # expect "senior python dev" to be highest (index 2)
    assert top[0]["job_key"] == "j2"
