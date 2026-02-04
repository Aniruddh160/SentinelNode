import faiss
import pickle
import numpy as np
from typing import List, Dict


class VectorStore:
    def __init__(self, embedding_dim: int):
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.metadata: List[Dict] = []

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]):
        self.index.add(embeddings)
        self.metadata.extend(metadatas)

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        scores, indices = self.index.search(
            np.array([query_embedding]), top_k
        )

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            item = self.metadata[idx].copy()
            item["score"] = float(score)
            results.append(item)

        return results

    # --------- Persistence ---------

    def save(self, index_path: str, metadata_path: str):
        """
        Save FAISS index and metadata to disk.
        """
        faiss.write_index(self.index, index_path)

        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self, index_path: str, metadata_path: str):
        """
        Load FAISS index and metadata from disk.
        """
        self.index = faiss.read_index(index_path)

        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
