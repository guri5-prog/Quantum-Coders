import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:7b"


def ask_llm(prompt):
    """Send prompt to Ollama and return response"""
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

    except Exception as e:
        return f"ERROR: {str(e)}"


def sanitize_code(output):
    """Remove unsafe patterns"""
    output = output.replace("eval(", "# removed eval(")
    output = output.replace("exec(", "# removed exec(")
    output = output.replace("__import__", "# blocked import")
    output = output.replace("os.system", "# blocked system call")
    return output


def extract_code_only(text):
    """Extract only actual Python code (handles ``` blocks)"""
    lines = text.split("\n")
    code_lines = []
    inside_code = False

    for line in lines:
        if "```" in line:
            inside_code = not inside_code
            continue

        if inside_code:
            code_lines.append(line)

    # fallback if no code block found
    if not code_lines:
        for line in lines:
            if "Explanation" in line or "explanation" in line:
                break
            code_lines.append(line)

    return "\n".join(code_lines).strip()


def generate_fixed_code(code, bugs, security):
    """Generate and sanitize fixed code"""

    prompt = f"""
You are a Python security expert.

Fix the given code safely.

STRICT RULES:
- Do NOT use eval()
- Do NOT use exec()
- Do NOT use os.system()
- Do NOT execute user input
- Keep solution simple and safe

OUTPUT:
- First: ONLY Python code
- Then: short explanation

INPUT CODE:
{code}

BUGS:
{bugs}

SECURITY ISSUES:
{security}
"""

    raw_output = ask_llm(prompt)

    print("\n📥 RAW MODEL OUTPUT:\n")
    print(raw_output)

    # Extract only code
    code_only = extract_code_only(raw_output)

    # Sanitize unsafe patterns
    safe_code = sanitize_code(code_only)

    return safe_code + "\n\n# Explanation: Unsafe operations removed and code simplified."


# ---------------- TEST ----------------

if __name__ == "__main__":
    print("🚀 Running CodeLlama advanced test...\n")

    sample_code = """
import os

username = input("Enter username: ")
password = input("Enter password: ")

query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"

print("Executing query:", query)

command = input("Enter command: ")
os.system(command)

eval("print('Hello')")
"""

    bugs = """
- Unsafe string concatenation for SQL query
- No input validation
- Poor error handling
"""

    security = """
- SQL Injection vulnerability
- Use of os.system allows command injection
- Use of eval allows arbitrary code execution
"""

    result = generate_fixed_code(sample_code, bugs, security)

    print("\n===== FINAL FIXED CODE =====\n")
    print(result)