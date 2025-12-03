# REFACTORING Summary

Implemented:
- SRP: split responsibilities into JobScraper, JobCleaner, IEmbeddingService, SimilarityCalculator, Pipeline.
- DIP: introduced IEmbeddingService and inject concrete embedder (OpenAI/Mock).

See source files in JobMatcher/ and tests in Tests/.
