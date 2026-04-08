import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

vector_store = None

def index_directory(path):

    global vector_store

    print("INDEXING DIRECTORY:", path)

    docs = []

    for root, dirs, files in os.walk(path):

        # skip unwanted folders
        dirs[:] = [d for d in dirs if d not in ["venv", "__pycache__", ".git"]]

        for file in files:

            file_path = os.path.join(root, file)

            print("Found file:", file_path)

            if file.endswith((".py", ".txt", ".md", ".json", ".yaml", ".yml")):

                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs.extend(loader.load())
                except Exception as e:
                    print("Skipping file:", file_path)

    print("Documents loaded:", len(docs))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    print("Chunks created:", len(chunks))

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(chunks, embeddings)

    print("FAISS index created")

    return len(chunks)