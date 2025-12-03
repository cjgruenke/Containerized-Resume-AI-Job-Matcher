# JobMatcher/embeddings.py

import numpy as np
from abc import ABC, abstractmethod

#
# 1. Embedding Interface (DIP)
#

class IEmbeddingService(ABC):
    @abstractmethod
    def embed_text(self, text: str):
        pass

    @abstractmethod
    def embed_texts(self, texts):
        pass


#
# 2. REAL Embedding Service (OpenAI or Gemini)
#    → USED BY YOUR APPLICATION
#

# Example OpenAI version — keep your actual working code here.
class OpenAIEmbeddingService(IEmbeddingService):
    def __init__(self, client, model="text-embedding-3-small"):
        self.client = client
        self.model = model

    def embed_text(self, text: str):
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_texts(self, texts):
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


#
# 3. MOCK Embedding Service (for tests only)
#    → USED ONLY INSIDE /Tests folder
#

class MockEmbeddingService(IEmbeddingService):
    """
    Deterministic mock that bases embeddings on text length.
    Ensures tests produce predictable similarity results.
    """
    def __init__(self, dim=4):
        self.dim = dim

    def _make_vec(self, text: str):
        length = len(text)
        base = length / 100.0
        return [base + (i * 0.01) for i in range(self.dim)]

    def embed_text(self, text: str):
        return self._make_vec(text)

    def embed_texts(self, texts):
        return [self._make_vec(t) for t in texts]
