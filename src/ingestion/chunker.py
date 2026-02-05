from typing import List, Dict
from sentence_transformers import SentenceTransformer


# Load once (important for performance)
_tokenizer_model = SentenceTransformer("all-MiniLM-L6-v2")
_tokenizer = _tokenizer_model.tokenizer


def chunk_text_tokens(
    text: str,
    chunk_size: int = 256,
    chunk_overlap: int = 64
) -> List[Dict]:
    """
    Chunk text based on tokens instead of characters.
    """

    tokens = _tokenizer.encode(text, add_special_tokens=False)
    chunks = []

    start = 0
    chunk_id = 0
    total_tokens = len(tokens)

    while start < total_tokens:
        end = start + chunk_size
        chunk_tokens = tokens[start:end]

        chunk_text = _tokenizer.decode(chunk_tokens, skip_special_tokens=True)

        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "start_token": start,
            "end_token": min(end, total_tokens)
        })

        chunk_id += 1
        start += chunk_size - chunk_overlap

    return chunks


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 256,
    chunk_overlap: int = 64
) -> List[Dict]:
    """
    Apply token-based chunking to documents.
    """

    all_chunks = []

    for doc in documents:
        doc_chunks = chunk_text_tokens(
            doc["text"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        for chunk in doc_chunks:
            all_chunks.append({
                "chunk_id": f"{doc['doc_id']}_{chunk['chunk_id']}",
                "doc_id": doc["doc_id"],
                "source": doc["source"],
                "text": chunk["text"],
                "start_token": chunk["start_token"],
                "end_token": chunk["end_token"]
            })

    for i, chunk in enumerate(all_chunks):
        chunk["chunk_id"] = i


    return all_chunks
