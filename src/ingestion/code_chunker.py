import ast

def chunk_python_file(file_dict):
    chunks = []

    tree = ast.parse(file_dict["content"])

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            chunks.append({
                "type": "function",
                "name": node.name,
                "file": file_dict["file_path"],
                "code": ast.get_source_segment(file_dict["content"], node)
            })

        elif isinstance(node, ast.ClassDef):
            chunks.append({
                "type": "class",
                "name": node.name,
                "file": file_dict["file_path"],
                "code": ast.get_source_segment(file_dict["content"], node)
            })

    return chunks
