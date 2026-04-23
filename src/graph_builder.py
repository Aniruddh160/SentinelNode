import ast
import os

def extract_imports(file_path):
    imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):

            # import x
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[-1])

            # from x.y import z
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[-1])

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
                if {"id": file} not in nodes:
                    nodes.append({"id": file})

    # Build edges
    for file_name, path in file_map.items():
        imports = extract_imports(path)

        for imp in imports:
            target_file = imp + ".py"
            node_ids = set(n["id"] for n in nodes)

            for imp in imports:
                target_file = imp + ".py"

                if target_file in node_ids:
                    edges.append({
                        "source": file_name + ".py",
                        "target": target_file
                    })

    return {"nodes": nodes, "edges": edges}