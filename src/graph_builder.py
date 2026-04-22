import os
import ast

def extract_imports(file_path):
    imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

    return imports


def build_graph(directory):
    nodes = []
    edges = []

    file_map = {}

    # Collect Python files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                file_map[file.replace(".py", "")] = full_path
                nodes.append({"id": file})

    # Build edges
    for file_name, path in file_map.items():
        imports = extract_imports(path)

        for imp in imports:
            target_file = imp + ".py"
            if target_file in [n["id"] for n in nodes]:
                edges.append({
                    "source": file_name + ".py",
                    "target": target_file
                })

    return {"nodes": nodes, "edges": edges}