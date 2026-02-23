from ingestion.code_loader import load_python_repo
from ingestion.code_chunker import chunk_python_file

# 👇 Change this to the repo you want to test
REPO_PATH = "src"


print("Loading Python repo...")
files = load_python_repo(REPO_PATH)

print(f"Found {len(files)} Python files\n")

all_chunks = []

for f in files:
    chunks = chunk_python_file(f)
    all_chunks.extend(chunks)

print(f"Extracted {len(all_chunks)} code chunks\n")

# Show first few chunks
for chunk in all_chunks[:5]:
    print("------")
    print("Type:", chunk["type"])
    print("Name:", chunk["name"])
    print("File:", chunk["file"])
    print("Code preview:\n", chunk["code"][:300])
