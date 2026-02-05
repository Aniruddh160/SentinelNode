from utils.silence import *

import os
from collections import defaultdict

from ingestion.loader import load_documents
from ingestion.chunker import chunk_documents
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from llm.synthesizer import AnswerSynthesizer
from retrieval.bm25 import BM25Index
from retrieval.graph import GraphIndex
from structure.graph_layer import graph_aware_retrieval
from evaluation.strategy_logger import log_strategy
from evaluation.graph_utility import compute_graph_utility
from evaluation.grounding import compute_grounding_coverage



# ---- Paths ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "sample_docs")
INDEX_DIR = os.path.join(BASE_DIR, "data", "index")

FAISS_INDEX_PATH = os.path.join(INDEX_DIR, "sentinel.index")
META_PATH = os.path.join(INDEX_DIR, "sentinel_meta.pkl")


# ---- Initialize ----
embedder = Embedder()

embedding_dim = embedder.embed_query("test").shape[1]
vector_store = VectorStore(embedding_dim)


# ---- Load or Build Index ----
if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(META_PATH):
    print("Loading existing FAISS index...")
    vector_store.load(FAISS_INDEX_PATH, META_PATH)
    chunks = vector_store.metadata  # needed for BM25

else:
    print("Building FAISS index...")
    docs = load_documents(DATA_DIR)
    chunks = chunk_documents(docs, chunk_size=128, chunk_overlap=32)

    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    # Ensure index directory exists
    os.makedirs(INDEX_DIR, exist_ok=True)

    vector_store.add(embeddings, chunks)
    vector_store.save(FAISS_INDEX_PATH, META_PATH)


    print("Index built and saved.")


# ---- Build BM25 Index ----
chunk_texts = [c["text"] for c in chunks]
bm25 = BM25Index(chunk_texts)
graph = GraphIndex(chunks)


# ---- Hybrid Re-ranker ----
def hybrid_rerank(vector_results, bm25_results, alpha=0.6):
    scores = defaultdict(float)
    texts = {}

    if vector_results:
        max_v = max(r["score"] for r in vector_results) or 1.0
        for r in vector_results:
            scores[r["text"]] += alpha * (r["score"] / max_v)
            texts[r["text"]] = r["text"]

    if bm25_results:
        max_b = max(r["score"] for r in bm25_results) or 1.0
        for r in bm25_results:
            scores[r["text"]] += (1 - alpha) * (r["score"] / max_b)
            texts[r["text"]] = r["text"]

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{"text": t, "score": s} for t, s in ranked]


# ---- Query ----
query = "Explain ingestion layer"

# ---- Graph-aware retrieval (NEW) ----
graph_result = graph_aware_retrieval(query, chunks)

graph_chunk_ids = graph_result.get("chunk_ids", [])

# If graph returned chunks, restrict search space
if graph_chunk_ids:
    graph_chunks = [c for c in chunks if c["chunk_id"] in graph_chunk_ids]
else:
    graph_chunks = chunks

log_strategy(
    query=query,
    strategy=graph_result.get("strategy"),
    chunk_ids=graph_chunk_ids
)


# Vector search
query_embedding = embedder.embed_query(query)
vector_results = vector_store.search(query_embedding, top_k=5)
if graph_chunk_ids:
    vector_results = [
        r for r in vector_results
        if r.get("chunk_id") in graph_chunk_ids
    ]
def extract_chunk_id(result):
    if "chunk_id" in result:
        return result["chunk_id"]
    if "metadata" in result and "chunk_id" in result["metadata"]:
        return result["metadata"]["chunk_id"]
    if "id" in result:
        return result["id"]
    return None


vector_chunk_ids = [
    extract_chunk_id(r)
    for r in vector_results
    if extract_chunk_id(r) is not None
]


# BM25 search
bm25 = BM25Index([c["text"] for c in graph_chunks])
bm25_results = bm25.search(query, top_k=5)

# Hybrid merge
hybrid_results = hybrid_rerank(vector_results, bm25_results, alpha=0.6)

contexts = [r["text"] for r in hybrid_results[:5]]

# ---- LLM Synthesis ----
synthesizer = AnswerSynthesizer()
answer = synthesizer.synthesize(query, contexts)
grounding = compute_grounding_coverage(answer, contexts)

print("\nGrounding Coverage:")
print(grounding)



utility = compute_graph_utility(
    graph_chunks=graph_chunk_ids,
    vector_chunks=vector_chunk_ids
)

print("Graph Utility:", utility)

print("\nRetrieval Strategy:", graph_result.get("strategy"))
print("Graph Chunk IDs:", graph_chunk_ids)

print("\nFinal Answer:\n")
print(answer)
print(chunks[0])
