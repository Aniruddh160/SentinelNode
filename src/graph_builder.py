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
    for i, e in enumerate(edges):
        e["id"] = i
    return {
        "nodes": nodes,
        "edges": edges
    }

def add_api_routes_to_graph(graph, symbol_data):
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    existing_ids = {n["id"] for n in nodes}

    for file_name, data in symbol_data.items():
        routes = data.get("routes", [])

        for r in routes:
            route_id = f"{r['method']} {r['path']}"

            # 🔹 Add route node
            if route_id not in existing_ids:
                nodes.append({
                    "id": route_id,
                    "label": route_id,
                    "type": "route"
                })
                existing_ids.add(route_id)

            # 🔹 Add function node
            func_id = f"{file_name}:{r['function']}"
            if func_id not in existing_ids:
                nodes.append({
                    "id": func_id,
                    "label": r["function"],
                    "type": "function"
                })
                existing_ids.add(func_id)

            # 🔹 Edge: route → function
            edges.append({
                "from": route_id,
                "to": func_id,
                "label": "calls"
            })

            # 🔹 Edge: function → file
            edges.append({
                "from": func_id,
                "to": file_name,
                "label": "defined_in"
            })

    return graph