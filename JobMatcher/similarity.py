# JobMatcher/similarity.py

import numpy as np

class SimilarityCalculator:
    def _to_np(self, v):
        return np.array(v, dtype=np.float32)

    def cosine_similarity(self, a, b):
        a = self._to_np(a)
        b = self._to_np(b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        sim = float(np.dot(a, b) / denom)
        # numerical safety
        return max(min(sim, 1.0), -1.0)

    def rank(self, jobs, resume_emb, top_n=10):
        """
        Rank jobs by cosine similarity to resume embedding.
        Returns a list of job dicts with 'similarity' attached.
        """
        resume_emb = self._to_np(resume_emb)

        scored = []
        for job in jobs:
            job_emb = self._to_np(job["embedding"])
            score = self.cosine_similarity(resume_emb, job_emb)
            # Attach similarity score to job for CLI
            job_with_score = dict(job)  # shallow copy
            job_with_score["similarity"] = score
            scored.append((score, job_with_score))

        # Sort descending by similarity score
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return job dicts only (with similarity attached)
        return [job for _, job in scored[:top_n]]