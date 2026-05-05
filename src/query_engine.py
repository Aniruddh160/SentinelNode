import requests
import os
import re
import json
import src.indexer as indexer

import re

def is_general_question(q):
    # no file mentioned + short casual text
    return not re.search(r'\.py', q) and len(q.split()) < 6



# ================= LOAD GRAPH =================
def load_graph():
    try:
        with open("graph.json", "r") as f:
            return json.load(f)
    except:
        return {"nodes": [], "edges": []}


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
            return "Something went wrong."

        return data["response"].strip()

    except Exception as e:
        print("General chat error:", e)
        return "Backend not responding."


# ================= RELATIONSHIP HANDLER =================
def handle_relationship_question(question):
    try:
        graph_data = load_graph()  # ✅ FIXED

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        if not nodes or not edges:
            return "Graph data not available. Please index a project first."

        # Build node map
        node_map = {}

        for n in nodes:
            node_id = n.get("id")
            label = n.get("label", "").lower()

            if node_id and label:
                node_map[node_id] = label

        # Extract filenames
        files = [f.strip() for f in re.findall(r'([\w\-]+\.py)', question.lower())]

        if len(files) < 2:
            return "Please mention at least two files."

        f1, f2 = files[0], files[1]

        matches = []

        impact_keywords = ["change", "modify", "affect", "impact", "break"]
        question_lower = question.lower()
        for e in edges:
            src = node_map.get(e["from"], "")
            dst = node_map.get(e["to"], "")
            relation = e.get("label", "related_to")

            # Check if these two files match
            def file_match(a, b):
                return a in b or b in a

            if (file_match(f1, src) and file_match(f2, dst)) or (file_match(f2, src) and file_match(f1, dst)):

                # 🔥 IMPACT MODE
                if any(k in question_lower for k in impact_keywords):

                    if relation == "import":
                        if f1 == src and f2 == dst:
                            changer = src
                            affected = dst
                        else:
                            changer = dst
                            affected = src

                        explanation = f"If you modify {changer}, it may affect {affected} because {affected} depends on it."

                        explanation += "\n\nPossible impacts:"
                        explanation += f"\n- If class/function names change → {src} may break"
                        explanation += f"\n- If method signatures change → runtime errors may occur"
                        explanation += f"\n- If logic changes → behavior of {src} may change"
                        explanation += f"\n- This is a direct dependency via {relation}"
                    else:
                        explanation = f"{src} is related to {dst} via '{relation}', so changes may impact it."

                # 🔹 NORMAL MODE
                else:
                    if relation == "import":
                        explanation = f"{src} imports {dst}, meaning it uses functions, classes, or variables defined in {dst}."
                    else:
                        explanation = f"{src} is related to {dst} via '{relation}'."

                matches.append(explanation)

        if not matches:
            return f"No direct relationship found between {f1} and {f2}."

        response = "Here's how the files are related:\n\n"

        for m in matches[:5]:
            response += f"- {m}\n"

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"


# ================= MAIN FUNCTION =================
def ask_question(question):

    question_lower = question.lower()
    if is_general_question(question):
        return "Hey 👋 Ask me something about your codebase!"
    # ================= CASUAL CHAT =================
    casual_keywords = [
        "hi", "hello", "hey", "how are you", "what's up",
        "who are you", "thanks", "thank you"
    ]

    if any(k in question_lower for k in casual_keywords):
        return general_chat(question)

    # ================= SYMBOL USAGE =================
    usage_keywords = ["where is", "used", "usage", "where exactly"]

    if any(k in question_lower for k in usage_keywords):
        result = handle_symbol_usage(question)
        if result:
            return result

    # ================= FILE RELATIONSHIP =================
    files = re.findall(r'([\w\-]+\.py)', question_lower)

    relationship_keywords = [
        "affect", "related", "connected", "depend",
        "used by", "impact", "relationship"
    ]

    if len(files) >= 2 or any(k in question_lower for k in relationship_keywords):
        return handle_relationship_question(question)

    # ================= GRAPH QUESTIONS =================
    graph_keywords = ["graph", "knowledge graph", "nodes", "edges", "connections"]

    if any(k in question_lower for k in graph_keywords):
        return general_chat(
            "Explain what a knowledge graph represents in a codebase in simple terms."
        )


    class_keywords = ["classes", "class list", "what are the classes"]

    if any(k in question_lower for k in class_keywords):
        result = handle_class_listing(question)
        if result:
            return result
        

    function_keywords = ["functions", "function list", "all functions"]

    if any(k in question_lower for k in function_keywords):
        result = handle_function_listing(question)
        if result:
            return result
        

    api_keywords = ["api routes", "endpoints", "routes", "api"]

    if any(k in question_lower for k in api_keywords):
        result = handle_api_routes(question)
        if result:
            return result
    

    # ================= CHECK INDEX =================
    if indexer.vector_store is None:
        return "No documents indexed."

    # ================= FILE-SPECIFIC RETRIEVAL =================
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

    # ================= SEMANTIC SEARCH =================
    if file_matches:
        docs = file_matches[:3]
    else:
        docs = indexer.vector_store.similarity_search(question, k=3)

    docs = [d for d in docs if len(d.page_content.strip()) > 50]

    if not docs:
        return "No relevant information found in indexed code."

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
                "options": {
                    "temperature": 0.2,
                    "num_predict": 300
                }
            },
            timeout=120
        )

        data = response.json()

    except requests.exceptions.Timeout:
        return "LLM timeout. Try again."

    except Exception as e:
        print("LLM error:", e)
        return "Backend not responding."

    if "response" not in data:
        print("LLM RAW OUTPUT:", data)
        return "LLM failed to generate a response."

    answer = data["response"].strip()

    if not answer:
        return "Empty response from LLM."

    if "NOT_FOUND" in answer:
        return "No relevant information found in indexed code."

    # ================= SOURCES =================
    source_text = "\n\nSources:\n"
    for src in list(sources)[:5]:
        source_text += f"- {src}\n"

    return answer + source_text


def load_symbols():
    try:
        with open("symbols.json", "r") as f:
            return json.load(f)
    except:
        return {}
    

def handle_symbol_usage(question):
    import re

    symbols = load_symbols()
    question_lower = question.lower()

    # extract file
    file_match = re.search(r'([\w\-]+\.py)', question_lower)
    if not file_match:
        return None

    file_name = file_match.group(1)

    # extract class name (simple heuristic: capitalized word)
    class_match = re.search(r'\b([A-Z][A-Za-z0-9_]*)\b', question)
    if not class_match:
        return None

    class_name = class_match.group(1)

    file_data = symbols.get(file_name)

    if not file_data:
        return f"No analysis found for {file_name}."

    usages = file_data.get("usages", {}).get(class_name)

    if not usages:
        return f"{class_name} is not used inside {file_name}."

    response = f"{class_name} is used in {file_name} at:\n\n"

    for u in usages:
        response += f"- Function `{u['function']}` (line {u['line']})\n"

    return response


def handle_class_listing(question):
    import re

    symbols = load_symbols()
    question_lower = question.lower()

    file_match = re.search(r'([\w\-]+\.py)', question_lower)
    if not file_match:
        return None

    file_name = file_match.group(1)

    file_data = symbols.get(file_name)

    if not file_data:
        return f"No analysis found for {file_name}."

    classes = file_data.get("classes", [])

    if not classes:
        return f"No classes found in {file_name}."

    response = f"Classes in {file_name}:\n\n"

    for c in classes:
        response += f"- {c['name']} (line {c['line']})\n"

    return response


def handle_function_listing(question):
    import re

    symbols = load_symbols()
    question_lower = question.lower()

    file_match = re.search(r'([\w\-]+\.py)', question_lower)
    if not file_match:
        return None

    file_name = file_match.group(1)

    file_data = symbols.get(file_name)

    if not file_data:
        return f"No analysis found for {file_name}."

    functions = file_data.get("functions", [])

    if not functions:
        return f"No functions found in {file_name}."

    response = f"Functions in {file_name}:\n\n"

    for f in functions:
        response += f"- {f['name']} (line {f['line']})\n"

    return response

def handle_api_routes(question):
    import re

    symbols = load_symbols()
    question_lower = question.lower()

    file_match = re.search(r'([\w\-]+\.py)', question_lower)
    if not file_match:
        return None

    file_name = file_match.group(1)

    file_data = symbols.get(file_name)

    if not file_data:
        return f"No analysis found for {file_name}."

    routes = file_data.get("routes", [])

    if not routes:
        return f"No API routes found in {file_name}."

    response = f"API routes in {file_name}:\n\n"

    for r in routes:
        response += f"- [{r['method']}] {r['path']} → `{r['function']}` (line {r['line']})\n"

    return response