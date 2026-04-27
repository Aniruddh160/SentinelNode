import os
import ast

def extract_imports(file_path):
    imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])

    return imports


def build_graph(project_path):
    nodes = []
    edges = []
    file_map = {}

    # 🔹 Step 1: Collect files
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                module = file.replace(".py", "")
                file_map[module] = file

    # 🔹 Step 2: Create nodes
    for module, file in file_map.items():
        nodes.append({
            "id": file,
            "label": file   # 🔥 IMPORTANT
        })

    # 🔹 Step 3: Create edges
    for module, file in file_map.items():
        file_path = None

        for root, _, files in os.walk(project_path):
            if file in files:
                file_path = os.path.join(root, file)
                break

        if not file_path:
            continue

        imports = extract_imports(file_path)

        for imp in imports:
            if imp in file_map:
                edges.append({
                    "from": file,
                    "to": file_map[imp],
                    "label": "import"
                })

    return {
        "nodes": nodes,
        "edges": edges
    }