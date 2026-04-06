from app.utils.parser import parse_code
import ast

def detect_dos(code: str):
    tree = parse_code(code)

    if not tree:
        return ["Parsing failed"]

    issues = []

    for node in ast.walk(tree):

        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value == True:
                issues.append("Infinite loop detected (DoS risk)")

        if isinstance(node, ast.For):
            if isinstance(node.iter, ast.Call):
                if getattr(node.iter.func, 'id', '') == 'range':
                    issues.append("Large loop may cause performance issues")

    return issues