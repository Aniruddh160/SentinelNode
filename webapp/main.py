from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from src.github_loader import clone_repo
from src.indexer import index_directory as run_indexer
from src.query_engine import ask_question
from src.graph_builder import build_graph
from src.graph_builder import extract_imports
import os
import json




app = FastAPI()

app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
templates = Jinja2Templates(directory="webapp/templates")


graph_data = {
    "nodes": [],
    "edges": []
}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/query")
async def query_llm(data: dict):

    question = data["question"]

    answer = ask_question(question)

    return {"answer": answer}


@app.post("/index-folder")
async def index_directory_api(data: dict):

    path = data["path"]

    if not os.path.exists(path):
        return {"status": "invalid path"}

    chunks = run_indexer(path)
    
    graph = build_graph(path)
    with open("graph.json", "w") as f:
        json.dump(graph, f)
    
    graph_data["nodes"] = graph.get("nodes", [])
    graph_data["edges"] = graph.get("edges", [])

    return {
        "status": "indexed",
        "chunks": chunks
    }

@app.post("/clone-repo")
async def clone_repo_api(data: dict):

    repo_url = data.get("repo_url")

    if not repo_url:
        return {"status": "error", "message": "No repo URL provided"}

    try:
        # Step 1: Clone repo
        local_path = clone_repo(repo_url)
        
        # Step 2: Reuse your existing indexer
        chunks = run_indexer(local_path)

        graph = build_graph(local_path)
        with open("graph.json", "w") as f:
            json.dump(graph, f)

        graph_data["nodes"] = graph.get("nodes", [])
        graph_data["edges"] = graph.get("edges", [])

        return {
            "status": "success",
            "message": "Repo cloned and indexed",
            "path": local_path,
            "chunks": chunks
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.get("/get-graph")
def get_graph():
    return graph_data