import os
import logging
from typing import List
from sentence_transformers import SentenceTransformer

# ---- Silence HuggingFace / Transformers noise ----
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(
            model_name,
            device="cpu"   # change to "cuda" later if needed
        )

    def embed_texts(self, texts: List[str]):
        """
        Convert a list of texts into embeddings.
        Returns: np.ndarray of shape (N, dim)
        """
        return self.model.encode(
            texts,
            show_progress_bar=False,      
            normalize_embeddings=True,
            convert_to_numpy=True
        )

    def embed_query(self, query: str):
        """
        Embed a single query.
        Returns: np.ndarray of shape (1, dim)
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        # Ensure FAISS-safe shape
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)

        return embedding
