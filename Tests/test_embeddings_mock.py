# tests/test_embeddings_mock.py
from JobMatcher.embeddings import MockEmbeddingService

def test_mock_embedding_dim_and_repeatability():
    svc = MockEmbeddingService(dim=8)
    a = svc.embed_text("hello world")
    b = svc.embed_text("hello world")
    assert len(a) == 8
    assert a == b
