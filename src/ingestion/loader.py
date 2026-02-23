import os
from typing import List, Dict
from pypdf import PdfReader


def load_text_file(file_path: str) -> str:
    """Load and clean a text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    return normalize_text(text)


def load_pdf_file(file_path: str) -> str:
    """Load and extract text from a PDF file."""
    reader = PdfReader(file_path)
    pages = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)

    return normalize_text("\n".join(pages))


def normalize_text(text: str) -> str:
    """Basic text cleaning."""
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")
    text = " ".join(text.split())
    return text.strip()


def load_documents(data_dir: str) -> List[Dict]:
    """
    Load all supported documents recursively from a directory.
    Returns a list of dicts with doc_id, source, and text.
    """
    documents = []

    for root, _, files in os.walk(data_dir):
        for filename in files:
            file_path = os.path.join(root, filename)

            if filename.lower().endswith((".txt", ".md")):
                text = load_text_file(file_path)

            elif filename.lower().endswith(".pdf"):
                text = load_pdf_file(file_path)

            else:
                continue

            if text:
                documents.append({
                    "doc_id": os.path.splitext(filename)[0],
                    "source": file_path,
                    "text": text
                })

    return documents
