import requests
import src.indexer as indexer


def ask_question(question):

    if indexer.vector_store is None:
        return "No documents indexed."

    docs = indexer.vector_store.similarity_search(question, k=4)

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
You are a senior software engineer analyzing a codebase.

Use the provided context to answer the question.

CONTEXT:
{context}

QUESTION:
{question}

Instructions:
- Be precise and technical
- Explain how the system works
- Mention dependencies between components
- If it's about changes, explain impact clearly
- Avoid generic explanations

Answer:
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

    print("OLLAMA RESPONSE:", data)  # debug

    if "response" in data:
        return data["response"]

    return "LLM returned an unexpected response."