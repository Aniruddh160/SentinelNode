from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.indexer import index_directory as run_indexer
from src.query_engine import ask_question

import os
app = FastAPI()

app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
templates = Jinja2Templates(directory="webapp/templates")


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


@app.post("/index-directory")
async def index_directory_api(data: dict):

    path = data["path"]

    if not os.path.exists(path):
        return {"status": "invalid path"}

    chunks = run_indexer(path)

    return {
        "status": "indexed",
        "chunks": chunks
    }