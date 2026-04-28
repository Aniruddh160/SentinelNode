import requests
import os
import src.indexer as indexer


# ================= GENERAL CHAT =================
def general_chat(question):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": f"""
You are a friendly assistant.

- Be natural and short
- No technical explanations unless asked

User: {question}
Assistant:
""",
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=300
        )

        data = response.json()

        if "response" not in data:
            return "Hey — something went wrong."

        return data["response"].strip()

    except Exception as e:
        print("General chat error:", e)
        return "⚠️ Backend not responding. Is Ollama running?"


# ================= MAIN FUNCTION =================
def ask_question(question):

    # ================= ROUTER =================
    casual_keywords = [
        "hi", "hello", "hey", "how are you", "what's up",
        "who are you", "thanks", "thank you"
    ]

    if any(k in question.lower() for k in casual_keywords):
        return general_chat(question)

    # ================= CHECK INDEX =================
    if indexer.vector_store is None:
        return "❌ No documents indexed."

    question_lower = question.lower()

# ================= HYBRID RETRIEVAL =================

    import re

    # 🔹 Extract filename from question
    file_query = None
    match = re.search(r'([\w\-]+\.py)', question_lower)

    if match:
        file_query = match.group(1)

    file_matches = []

    if file_query:
        try:
            for doc in indexer.vector_store.docstore._dict.values():
                source = os.path.basename(doc.metadata.get("source", "")).lower()

                if file_query == source:
                    file_matches.append(doc)
        except Exception as e:
            print("File match error:", e)

    # 🔹 Fallback to semantic search
    if file_matches:
        docs = file_matches[:3]
    else:
        docs = indexer.vector_store.similarity_search(question, k=3)

    # ================= CONTEXT BUILD =================
    context_blocks = []
    sources = set()

    for d in docs:
        src = os.path.basename(d.metadata.get("source", "unknown"))
        sources.add(src)

        block = f"[FILE: {src}]\n{d.page_content.strip()}"
        context_blocks.append(block)

    context = "\n\n---\n\n".join(context_blocks)

    # ================= PROMPT =================
    prompt = f"""
You are a strict code analysis engine.

RULES:
- ONLY use the provided context
- DO NOT guess
- If not found, output EXACTLY: NOT_FOUND

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    # ================= LLM CALL =================
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=300
        )

        data = response.json()

    except Exception as e:
        print("LLM error:", e)
        return "⚠️ Backend not responding."

    if "response" not in data:
        return "❌ LLM returned an unexpected response."

    answer = data["response"].strip()

    if "NOT_FOUND" in answer:
        return "❌ No relevant information found in indexed code."

    # ================= SOURCES =================
    source_text = "\n\n📂 Sources:\n"
    for src in list(sources)[:5]:
        source_text += f"- {src}\n"

    return answer + source_text