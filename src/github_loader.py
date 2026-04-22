import tempfile
from git import Repo

def clone_repo(repo_url: str) -> str:
    """
    Clone GitHub repo to temp directory
    """
    temp_dir = tempfile.mkdtemp(prefix="repo_")

    try:
        Repo.clone_from(repo_url, temp_dir)
        return temp_dir
    except Exception as e:
        raise Exception(f"Clone failed: {str(e)}")