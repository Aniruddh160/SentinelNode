import os

from ingestion.loader import load_documents
from ingestion.chunker import chunk_documents
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore


# ---- Paths ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "sample_docs")
INDEX_DIR = os.path.join(BASE_DIR, "data", "index")

FAISS_INDEX_PATH = os.path.join(INDEX_DIR, "sentinel.index")
META_PATH = os.path.join(INDEX_DIR, "sentinel_meta.pkl")


# ---- Initialize ----
embedder = Embedder()

# We know embedding dim from the model
embedding_dim = embedder.embed_query("test").shape[0]
vector_store = VectorStore(embedding_dim)


# ---- Load or Build Index ----
if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(META_PATH):
    print("Loading existing FAISS index...")
    vector_store.load(FAISS_INDEX_PATH, META_PATH)

else:
    print("Building FAISS index...")
    docs = load_documents(DATA_DIR)
    chunks = chunk_documents(docs, chunk_size=128, chunk_overlap=32)

    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    vector_store.add(embeddings, chunks)
    vector_store.save(FAISS_INDEX_PATH, META_PATH)

    print("Index built and saved.")


# ---- Query ----
query = "What is SentinelNode?"
query_embedding = embedder.embed_query(query)

results = vector_store.search(query_embedding, top_k=3)

print("\nTop results:")
for res in results:
    print(f"\nScore: {res['score']:.4f}")
    print(res["text"])
