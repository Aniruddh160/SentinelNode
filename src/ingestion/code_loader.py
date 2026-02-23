import os

def load_python_repo(repo_path):
    code_files = []

    EXCLUDE_DIRS = {"venv", "__pycache__", ".git"}

    for root, dirs, files in os.walk(repo_path):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    code_files.append({
                        "file_path": full_path,
                        "file_name": file,
                        "content": content
                    })

                except Exception:
                    pass  # silently skip unreadable files

    return code_files

