from typing import List, Dict
import os
import numpy as np


try:
    from sentence_transformers import SentenceTransformer

    _SENTENCE_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    _SENTENCE_MODEL = None


OPENAI_KEY = os.getenv("OPENAI_API_KEY")


def _cosine(a: List[float], b: List[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def get_embeddings(texts: List[str]) -> List[List[float]]:
    if _SENTENCE_MODEL is not None:
        return _SENTENCE_MODEL.encode(
            texts, show_progress_bar=False, convert_to_numpy=True
        ).tolist()

    if OPENAI_KEY:
        import requests

        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json",
        }
        # using text-embedding-3-small or text-embedding-3-large can be appropriate
        data = {"model": "text-embedding-3-small", "input": texts}
        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()
        payload = r.json()
        return [item["embedding"] for item in payload["data"]]

    raise RuntimeError(
        """No sentence-transformers installed and OPENAI_API_KEY not set. Install sentence-transformers or set OPENAI_API_KEY."""
    )


def evaluate_answers(refs: List[str], answers: List[str]) -> List[Dict]:
    texts = refs + answers
    embs = get_embeddings(texts)
    ref_embs = embs[: len(refs)]
    ans_embs = embs[len(refs) :]

    results = []
    for i, (r_emb, a_emb) in enumerate(zip(ref_embs, ans_embs)):
        sim = _cosine(r_emb, a_emb)
        grade = max(0.0, min(100.0, (sim + 1) / 2 * 100))
        results.append(
            {
                "question_idx": i,
                "similarity": sim,
                "grade": grade,
            }
        )
    return results
