import ast
import os


def analyze_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code)
    defined_classes = set()
    functions = []
    routes = []
    imports = {}
    usages = {}
    classes = []

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.current_function = "global"

        def visit_ImportFrom(self, node):
            module = node.module
            for name in node.names:
                symbol = name.name
                alias = name.asname
                imports[symbol] = {"module": module, "alias": alias}

        def visit_FunctionDef(self, node):
            # Check decorators for FastAPI routes
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if hasattr(decorator.func, "attr"):
                        method = decorator.func.attr  # get, post, etc.

                        if method in ["get", "post", "put", "delete", "patch"]:
                            if decorator.args:
                                path = None
                                if isinstance(decorator.args[0], ast.Constant):
                                    path = decorator.args[0].value

                                routes.append({
                                    "function": node.name,
                                    "method": method.upper(),
                                    "path": path,
                                    "line": node.lineno
                                })

            # ALSO keep your existing function tracking
            functions.append({
                "name": node.name,
                "line": node.lineno
            })

            prev = self.current_function
            self.current_function = node.name
            self.generic_visit(node)
            self.current_function = prev

        def visit_ClassDef(self, node):
            defined_classes.add(node.name)

            classes.append({
                "name": node.name,
                "line": node.lineno
            })

            self.generic_visit(node)

        def visit_Name(self, node):
            all_symbols = list(imports.keys()) + list(defined_classes)

            for symbol in all_symbols:
                if node.id == symbol:
                    usages.setdefault(symbol, []).append({
                        "function": self.current_function,
                        "line": node.lineno
                    })

            self.generic_visit(node)



        def visit_Constant(self, node):
            if isinstance(node.value, str):
                all_symbols = list(imports.keys()) + list(defined_classes)

                for symbol in all_symbols:
                    if node.value == symbol:
                        usages.setdefault(symbol, []).append({
                            "function": self.current_function,
                            "line": node.lineno
                        })
    Visitor().visit(tree)

    return {
        "imports": imports,
        "usages": usages,
        "classes": classes,
        "functions": functions,
        "routes": routes  
    }


def analyze_project(root_dir):
    result = {}

    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    result[f] = analyze_file(path)
                except Exception as e:
                    print(f"Error analyzing {f}: {e}")

    return result