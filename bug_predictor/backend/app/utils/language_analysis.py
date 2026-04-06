import re


SUPPORTED_LANGUAGES = {"python", "java", "javascript", "cpp"}


def normalize_language(language):
    value = str(language or "python").strip().lower()
    aliases = {
        "py": "python",
        "js": "javascript",
        "node": "javascript",
        "c++": "cpp",
        "cxx": "cpp",
        "cc": "cpp",
    }
    mapped = aliases.get(value, value)
    return mapped if mapped in SUPPORTED_LANGUAGES else "python"


def has_python_ast_support(language):
    return normalize_language(language) == "python"


def language_label(language):
    normalized = normalize_language(language)
    labels = {
        "python": "Python",
        "java": "Java",
        "javascript": "JavaScript",
        "cpp": "C++",
    }
    return labels.get(normalized, "Python")


def language_extension(language):
    normalized = normalize_language(language)
    return {
        "python": ".py",
        "java": ".java",
        "javascript": ".js",
        "cpp": ".cpp",
    }.get(normalized, ".py")


def extract_generic_features(code):
    lines = [line for line in code.splitlines() if line.strip()]
    text = "\n".join(lines)
    functions = len(re.findall(r"\b(def|function)\b", text))
    functions += len(re.findall(r"\b[A-Za-z_]\w*\s+[A-Za-z_]\w*\s*\([^;)]*\)\s*\{", text))
    loops = len(re.findall(r"\b(for|while)\b", text))
    assignments = len(re.findall(r"(?<![=!<>])=(?!=)", text))
    imports = re.findall(r"\b(import|include|from)\b", text)
    return {
        "functions": functions,
        "loops": loops,
        "assignments": assignments,
        "imports": imports,
        "function_names": [],
    }


def detect_generic_bugs(code, language):
    normalized = normalize_language(language)
    issues = []

    _append_pattern_issues(
        issues,
        code,
        r"\bif\s*\([^)]*=[^=][^)]*\)",
        "warning",
        "assignment-in-condition",
        "Possible assignment inside conditional expression",
    )
    _append_pattern_issues(
        issues,
        code,
        r"\bcatch\s*\([^)]*\)\s*\{\s*\}",
        "warning",
        "empty-catch",
        "Empty catch block may hide failures",
    )

    if normalized == "javascript":
        _append_pattern_issues(
            issues,
            code,
            r"\bvar\b",
            "refactor",
            "prefer-let-const",
            "Use let/const instead of var to avoid scope bugs",
        )
    elif normalized == "java":
        _append_pattern_issues(
            issues,
            code,
            r"\bSystem\.out\.println\s*\(",
            "refactor",
            "debug-print",
            "Debug print statement found in source code",
        )
    elif normalized == "cpp":
        _append_pattern_issues(
            issues,
            code,
            r"\b(NULL)\b",
            "warning",
            "legacy-null",
            "Prefer nullptr over NULL in modern C++",
        )

    return issues


def detect_generic_security(code, language):
    normalized = normalize_language(language)
    issues = []

    _append_security(
        issues,
        code,
        r"\beval\s*\(",
        "dynamic_eval",
        "HIGH",
        "Code evaluation detected",
    )
    _append_security(
        issues,
        code,
        r"\b(exec|system|popen|Runtime\.getRuntime\(\)\.exec)\s*\(",
        "command_execution",
        "HIGH",
        "Command execution sink detected",
    )
    _append_security(
        issues,
        code,
        r"(password|secret|token|api[_-]?key)\s*[:=]\s*['\"][^'\"]{6,}['\"]",
        "hardcoded_secret",
        "MEDIUM",
        "Potential hardcoded secret detected",
    )

    if normalized in {"java", "javascript", "cpp"}:
        _append_security(
            issues,
            code,
            r"(SELECT|INSERT|UPDATE|DELETE).*(\+|\$\{)",
            "sql_injection",
            "HIGH",
            "Possible SQL injection via string concatenation",
        )

    if normalized == "cpp":
        _append_security(
            issues,
            code,
            r"\b(gets|strcpy|sprintf)\s*\(",
            "unsafe_c_api",
            "HIGH",
            "Unsafe C/C++ API usage detected",
        )

    return issues


def detect_generic_anomalies(code, language):
    issues = []
    features = extract_generic_features(code)

    if features["loops"] >= 3 and features["functions"] == 0:
        issues.append({
            "type": "Complex Control Flow",
            "message": "High loop usage without function boundaries",
            "severity": "MEDIUM",
        })

    _append_anomaly(
        issues,
        code,
        r"\bTODO\b|\bFIXME\b",
        "Unresolved Marker",
        "TODO/FIXME markers left in code",
        "LOW",
    )
    _append_anomaly(
        issues,
        code,
        r"\b(if|while|for)\s*\([^)]+\)\s*\{[^{}]{0,140}\}",
        "Compact Branch",
        "Single-line branch body may reduce readability",
        "LOW",
    )
    return issues


def detect_generic_dos(code, language):
    issues = []
    _append_dos(
        issues,
        code,
        r"\bwhile\s*\(\s*true\s*\)",
        "Potential infinite loop detected",
    )
    _append_dos(
        issues,
        code,
        r"\bfor\s*\(\s*;\s*;\s*\)",
        "Potential infinite for-loop detected",
    )
    _append_dos(
        issues,
        code,
        r"\bwhile\s+True\s*:",
        "Potential infinite loop detected",
    )
    return issues


def _line_number(code, position):
    return code.count("\n", 0, position) + 1


def _append_pattern_issues(issues, code, pattern, issue_type, symbol, message):
    for match in re.finditer(pattern, code, flags=re.IGNORECASE | re.MULTILINE):
        issues.append({
            "type": issue_type,
            "symbol": symbol,
            "message": message,
            "line": _line_number(code, match.start()),
            "column": 1,
        })


def _append_security(issues, code, pattern, issue_type, severity, message):
    for match in re.finditer(pattern, code, flags=re.IGNORECASE | re.MULTILINE):
        issues.append({
            "type": issue_type,
            "severity": severity,
            "confidence": "MEDIUM",
            "message": message,
            "line": _line_number(code, match.start()),
        })


def _append_anomaly(issues, code, pattern, issue_type, message, severity):
    if re.search(pattern, code, flags=re.IGNORECASE | re.MULTILINE):
        issues.append({
            "type": issue_type,
            "message": message,
            "severity": severity,
        })


def _append_dos(issues, code, pattern, message):
    if re.search(pattern, code, flags=re.IGNORECASE | re.MULTILINE):
        issues.append(message)
