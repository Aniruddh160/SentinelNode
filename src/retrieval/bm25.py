from rank_bm25 import BM25Okapi
import re

def tokenize(text: str):
    return re.findall(r"\w+", text.lower())

class BM25Index:
    def __init__(self, texts):
        self.texts = texts
        self.tokens = [tokenize(t) for t in texts]
        self.bm25 = BM25Okapi(self.tokens)

    def search(self, query: str, top_k=5):
        q_tokens = tokenize(query)
        scores = self.bm25.get_scores(q_tokens)
        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return [
            {"idx": i, "score": float(s), "text": self.texts[i]}
            for i, s in ranked
        ]
