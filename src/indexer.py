import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

vector_store = None

# ✅ Allowed file types
ALLOWED_EXTENSIONS = (
    ".py", ".js", ".ts", ".java", ".cpp",
    ".txt", ".md", ".json", ".yaml", ".yml"
)

# ❌ Folders to ignore
IGNORE_FOLDERS = [
    "venv", "__pycache__", ".git", "node_modules", "dist", "build"
]

# 🚫 Max file size (200KB)
MAX_FILE_SIZE = 200 * 1024


def is_valid_file(file_path):
    try:
        return os.path.getsize(file_path) <= MAX_FILE_SIZE
    except:
        return False


def index_directory(path):

    global vector_store

    print("INDEXING DIRECTORY:", path)

    docs = []
    total_files = 0

    for root, dirs, files in os.walk(path):

        # 🚫 Remove unwanted folders
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for file in files:

            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1]

            # ✅ Filter files
            if ext in ALLOWED_EXTENSIONS and is_valid_file(file_path):

                total_files += 1
                print("Indexing:", file_path)

                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                    loaded_docs = loader.load()

                    # 🧠 Add metadata
                    for doc in loaded_docs:
                        doc.metadata["source"] = file_path
                        doc.metadata["filename"] = file

                    docs.extend(loaded_docs)

                except Exception as e:
                    print("Skipped:", file_path)

    print(f"✅ Total valid files indexed: {total_files}")
    print("📄 Documents loaded:", len(docs))

    # ✂️ Better chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(docs)

    print("🧩 Chunks created:", len(chunks))

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(chunks, embeddings)

    print("🚀 FAISS index created successfully")

    return len(chunks)