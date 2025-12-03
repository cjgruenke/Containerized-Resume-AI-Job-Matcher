from JobMatcher.embeddings import MockEmbeddingService
from JobMatcher.similarity import SimilarityCalculator

mock = MockEmbeddingService(dim=4)

texts = ["python developer", "accountant", "senior python dev"]
embs = mock.embed_texts(texts)

resume = mock.embed_text("senior python developer")

sim = SimilarityCalculator()

print("RESUME:", resume)
print()

for i, (t, e) in enumerate(zip(texts, embs)):
    print(f"JOB {i}: {t}")
    print("embedding:", e)
    print("similarity:", sim.cosine_similarity(resume, e))
    print()
