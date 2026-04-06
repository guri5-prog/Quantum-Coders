import ast

from app.utils.parser import parse_code


LARGE_RANGE_THRESHOLD = 10 ** 7


def _constant_int(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def detect_dos(code: str):
    tree = parse_code(code)

    if not tree:
        return ["Parsing failed"]

    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                issues.append("Infinite loop detected (DoS risk)")

        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            if getattr(node.iter.func, "id", "") == "range":
                args = node.iter.args
                if args:
                    stop_node = args[0] if len(args) == 1 else args[1]
                    stop_value = _constant_int(stop_node)
                    if stop_value is not None and stop_value >= LARGE_RANGE_THRESHOLD:
                        issues.append("Extremely large range loop detected")

    return issues
