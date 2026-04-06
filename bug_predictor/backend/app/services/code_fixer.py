import requests
import re

from ..utils.language_analysis import language_label, normalize_language

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:7b"


def ask_llm(prompt: str):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2048
                }
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def sanitize_code(output: str):
    output = output.replace("eval(", "# removed eval(")
    output = output.replace("exec(", "# removed exec(")
    output = output.replace("__import__", "# blocked import")
    output = output.replace("os.system", "# blocked system call")
    return output


def extract_code_only(text: str):
    lines = text.split("\n")
    code_lines = []
    inside_code = False

    for line in lines:
        if "```" in line:
            inside_code = not inside_code
            continue

        if inside_code:
            code_lines.append(line)

    if not code_lines:
        for line in lines:
            if "Explanation" in line or "explanation" in line:
                break
            code_lines.append(line)

    return "\n".join(code_lines).strip()


def _format_findings(items):
    if not items:
        return "- None"

    rendered = []
    for item in items:
        message = item.get("message") or item.get("type") or "Issue detected"
        line = item.get("line")
        prefix = f"Line {line}: " if line else ""
        rendered.append(f"- {prefix}{message}")

    return "\n".join(rendered)


def _validate_fixed_code(code: str, language: str):
    common_rules = [
        (r"\beval\s*\(", "Use of eval() is unsafe."),
        (r"\bexec\s*\(", "Use of exec() is unsafe."),
        (r"\bos\.system\s*\(", "Use of os.system() is unsafe."),
        (r"\bRuntime\.getRuntime\(\)\.exec\s*\(", "Runtime command execution is unsafe."),
        (r"\b(gets|strcpy|sprintf)\s*\(", "Unsafe C/C++ APIs detected."),
    ]

    language_rules = {
        "python": [
            (r"\bsubprocess\.(run|Popen|call|check_output)\s*\([^)]*shell\s*=\s*True", "Shell execution in subprocess is unsafe."),
        ],
        "javascript": [
            (r"\bchild_process\.(exec|execSync)\s*\(", "Node child_process exec sink detected."),
        ],
        "cpp": [
            (r"\bsystem\s*\(", "C/C++ system() command execution is unsafe."),
            (r"\bpopen\s*\(", "C/C++ popen() command execution is unsafe."),
        ],
    }

    violations = []
    combined_rules = common_rules + language_rules.get(language, [])
    for pattern, message in combined_rules:
        if re.search(pattern, code, flags=re.IGNORECASE | re.MULTILINE):
            violations.append(message)
    return violations


def generate_fixed_code(code: str, bugs, security, language="python"):
    normalized_language = normalize_language(language)
    target_language = language_label(normalized_language)
    prompt = f"""
You are a {target_language} security expert.

Fix the given code safely.

STRICT RULES:
- Do NOT use eval()
- Do NOT use exec()
- Do NOT use os.system()
- Do NOT execute user input as code or shell commands
- Keep the solution simple, valid, and safe

OUTPUT:
- Return {target_language} code only

INPUT CODE:
{code}

BUGS:
{_format_findings(bugs)}

SECURITY ISSUES:
{_format_findings(security)}
"""

    raw_output = ask_llm(prompt)
    if raw_output.startswith("ERROR:"):
        return {
            "code": "",
            "status": "unavailable",
            "message": raw_output
        }

    code_only = extract_code_only(raw_output)
    safe_code = sanitize_code(code_only) if normalized_language == "python" else code_only

    if not safe_code:
        return {
            "code": "",
            "status": "empty",
            "message": "The fixer did not return usable code."
        }

    violations = _validate_fixed_code(safe_code, normalized_language)
    if violations:
        return {
            "code": "",
            "status": "rejected_unsafe",
            "message": "Generated fix failed safety validation: " + "; ".join(violations),
        }

    return {
        "code": safe_code,
        "status": "success",
        "message": "Fixed code generated successfully."
    }
