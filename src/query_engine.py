import requests
import os
import src.indexer as indexer


def ask_question(question):

    if indexer.vector_store is None:
        return "❌ No documents indexed."

    # 🔍 Retrieve more context
    docs = indexer.vector_store.similarity_search(question, k=5)

    # 🧠 Build context
    context = "\n\n".join([d.page_content for d in docs])

    # 📂 Extract sources
    sources = set()
    for d in docs:
        if "source" in d.metadata:
            sources.add(d.metadata["source"])

    # 🔥 Clean source names (optional but nicer)
    clean_sources = [os.path.basename(s) for s in sources]

    # 🧠 Improved prompt
    prompt = f"""
You are a senior software engineer analyzing a codebase.

STRICT RULES:
- Answer ONLY using the provided context
- Do NOT hallucinate
- If unsure, say "Not enough information"
- ALWAYS wrap code in triple backticks
- Use format:
```python
code here
- Never write "python" outside the code block
CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- Be precise and technical
- Explain flow of logic
- Mention relationships between files/components
- Keep answer structured

ANSWER:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    if "response" not in data:
        return "❌ LLM returned an unexpected response."

    answer = data["response"]

    # 📂 Append sources
    source_text = "\n\n📂 Sources:\n"
    for src in clean_sources[:5]:
        source_text += f"- {src}\n"

    return answer.strip() + source_text