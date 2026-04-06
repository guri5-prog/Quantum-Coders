import ast

# -------------------------------
# 1. Parse Code into AST
# -------------------------------
def parse_code(code: str):
    try:
        tree = ast.parse(code)
        return tree
    except Exception:
        return None


# -------------------------------
# 2. Extract Structural Features
# -------------------------------
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


# -------------------------------
# 3. Detect Dangerous Calls
# -------------------------------
def detect_dangerous_calls(tree, code_lines):
    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):

            func_name = None

            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in ["eval", "exec"]:
               issues.append({
                                "type": "Dangerous Function",
                                "message": "eval() is unsafe",
                                "severity": "HIGH",
                                "line": node.lineno,
                                "code": code_lines[node.lineno - 1]
})

            if func_name in ["system", "popen"]:
                issues.append({
                    "type": "Command Injection",
                    "message": "OS command execution detected",
                    "line": node.lineno,
                    "code": code_lines[node.lineno - 1]
                })

    return issues


# -------------------------------
# 4. Detect Hardcoded Secrets
# -------------------------------
def detect_secrets(tree, code_lines):
    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):

            if isinstance(node.value, ast.Constant):
                value = str(node.value.value).lower()

                if any(k in value for k in ["password", "secret", "api_key"]):
                    issues.append({
                        "type": "Hardcoded Secret",
                        "message": "Sensitive data hardcoded",
                        "line": node.lineno,
                        "code": code_lines[node.lineno - 1]
                    })

    return issues


# -------------------------------
# 5. Detect SQL Injection (AST-based)
# -------------------------------
def detect_sql_injection(tree, code_lines):
    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            issues.append({
                "type": "SQL Injection Risk",
                "message": "String concatenation detected",
                "line": node.lineno,
                "code": code_lines[node.lineno - 1]
            })

    return issues


# -------------------------------
# 6. MASTER FUNCTION
# -------------------------------
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