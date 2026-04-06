import requests


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


def generate_fixed_code(code: str, bugs, security):
    prompt = f"""
You are a Python security expert.

Fix the given code safely.

STRICT RULES:
- Do NOT use eval()
- Do NOT use exec()
- Do NOT use os.system()
- Do NOT execute user input as code or shell commands
- Keep the solution simple, valid, and safe

OUTPUT:
- Return Python code only

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
    safe_code = sanitize_code(code_only)

    if not safe_code:
        return {
            "code": "",
            "status": "empty",
            "message": "The fixer did not return usable code."
        }

    return {
        "code": safe_code,
        "status": "success",
        "message": "Fixed code generated successfully."
    }
