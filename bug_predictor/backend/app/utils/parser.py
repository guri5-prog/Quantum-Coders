import ast


def parse_code(code: str):
    try:
        return ast.parse(code)
    except Exception:
        return None


def extract_features(tree):
    features = {
        "functions": 0,
        "loops": 0,
        "imports": [],
        "function_names": [],
        "assignments": 0
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            features["functions"] += 1
            features["function_names"].append(node.name)
        elif isinstance(node, (ast.For, ast.While)):
            features["loops"] += 1
        elif isinstance(node, ast.Import):
            for alias in node.names:
                features["imports"].append(alias.name)
        elif isinstance(node, ast.Assign):
            features["assignments"] += 1

    return features


def detect_dangerous_calls(tree, code_lines):
    issues = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in ["eval", "exec"]:
            issues.append({
                "type": "Dangerous Function",
                "message": f"{func_name}() is unsafe",
                "severity": "HIGH",
                "line": node.lineno,
                "code": code_lines[node.lineno - 1]
            })

        if func_name in ["system", "popen"]:
            issues.append({
                "type": "Command Injection",
                "message": "OS command execution detected",
                "severity": "HIGH",
                "line": node.lineno,
                "code": code_lines[node.lineno - 1]
            })

    return issues


def _assigned_names(node):
    names = []
    for target in node.targets:
        if isinstance(target, ast.Name):
            names.append(target.id.lower())
    return names


def detect_secrets(tree, code_lines):
    issues = []
    secret_name_markers = ["password", "passwd", "secret", "token", "api_key", "apikey", "private_key"]
    placeholder_values = {"changeme", "your_api_key", "example", "demo", "sample", "test"}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue

        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            continue

        assigned_names = _assigned_names(node)
        if not assigned_names:
            continue

        if not any(marker in name for name in assigned_names for marker in secret_name_markers):
            continue

        value = node.value.value.strip()
        lowered_value = value.lower()

        if lowered_value in placeholder_values or lowered_value.startswith(("http://", "https://")):
            continue

        issues.append({
            "type": "Hardcoded Secret",
            "message": "Sensitive credential-like value hardcoded",
            "severity": "HIGH",
            "line": node.lineno,
            "code": code_lines[node.lineno - 1]
        })

    return issues


def _flatten_string_add(node):
    parts = []

    def visit(expr):
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            visit(expr.left)
            visit(expr.right)
        else:
            parts.append(expr)

    visit(node)
    return parts


def _is_user_controlled(expr):
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "input":
        return True
    if isinstance(expr, ast.JoinedStr):
        return any(isinstance(value, ast.FormattedValue) for value in expr.values)
    if isinstance(expr, ast.Name):
        return True
    return False


def detect_sql_injection(tree, code_lines):
    issues = []
    sql_keywords = ("select", "insert", "update", "delete", "where", "from", "join")

    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
            continue

        parts = _flatten_string_add(node)
        constant_text = " ".join(
            part.value.lower()
            for part in parts
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )

        if not any(keyword in constant_text for keyword in sql_keywords):
            continue

        if not any(_is_user_controlled(part) for part in parts):
            continue

        issues.append({
            "type": "SQL Injection Risk",
            "message": "SQL query built with string concatenation",
            "severity": "HIGH",
            "line": node.lineno,
            "code": code_lines[node.lineno - 1]
        })

    return issues


def analyze_ast(code: str):
    tree = parse_code(code)

    if not tree:
        return {
            "error": "Code parsing failed",
            "features": {},
            "issues": []
        }

    code_lines = code.split("\n")
    features = extract_features(tree)

    issues = []
    issues.extend(detect_dangerous_calls(tree, code_lines))
    issues.extend(detect_secrets(tree, code_lines))
    issues.extend(detect_sql_injection(tree, code_lines))

    return {
        "features": features,
        "issues": issues
    }
