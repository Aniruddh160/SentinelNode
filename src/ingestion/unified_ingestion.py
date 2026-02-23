from ingestion.loader import load_documents
from ingestion.chunker import chunk_documents
from ingestion.code_loader import load_python_repo
from ingestion.code_chunker import chunk_python_file

def build_unified_chunks(doc_path, code_path):
    chunk_id = 0
    all_chunks = []

    # ---- DOCUMENTS ----
    docs = load_documents(doc_path)
    doc_chunks = chunk_documents(docs, chunk_size=128, chunk_overlap=32)

    for c in doc_chunks:
        all_chunks.append({
            "chunk_id": chunk_id,
            "text": c["text"],
            "source_type": "doc",
            "file_path": c.get("source", "unknown"),
            "name": c.get("doc_id", "document")
        })
        chunk_id += 1

    # ---- CODE ----
    code_files = load_python_repo(code_path)

    for f in code_files:
        code_chunks = chunk_python_file(f)

        for c in code_chunks:
            all_chunks.append({
                "chunk_id": chunk_id,
                "text": f"{c['type']} {c['name']} in {c['file']}\n\n{c['code']}",
                "source_type": "code",
                "file_path": c["file"],
                "name": c["name"]
            })
            chunk_id += 1

    return all_chunks
