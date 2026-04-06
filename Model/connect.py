import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:7b"


# ---------------- LLM CALL ----------------
def ask_llm(prompt):
    for attempt in range(2):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 1024
                    }
                },
                timeout=300
            )

            response.raise_for_status()
            return response.json().get("response", "").strip()

        except requests.exceptions.Timeout:
            print("⚠️ Timeout... retrying")

    return "❌ LLM failed after retry"


# ---------------- SMART SANITIZER ----------------
def sanitize_code(output):
    """Replace unsafe code with safe, runnable alternatives"""

    # eval → safe parsing
    output = re.sub(
        r"\beval\s*\((.*?)\)",
        r"import ast\nast.literal_eval(\1)",
        output
    )

    # exec → block safely
    output = re.sub(
        r"\bexec\s*\(.*?\)",
        'print("Execution blocked for safety")',
        output
    )

    # os.system → disable
    output = re.sub(
        r"os\.system\s*\(.*?\)",
        'print("System command execution disabled")',
        output
    )

    # subprocess → disable
    output = re.sub(
        r"subprocess\.[a-zA-Z_]+\s*\(.*?\)",
        'print("Subprocess execution disabled")',
        output
    )

    # pickle.loads → block
    output = re.sub(
        r"pickle\.loads\s*\(.*?\)",
        'print("Unsafe deserialization blocked")',
        output
    )

    # dangerous import
    output = re.sub(
        r"__import__",
        "# blocked import",
        output
    )

    return output


# ---------------- EXTRACTION ----------------
def extract_code_only(text):
    """Extract only Python code cleanly"""

    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()

    cleaned = []
    for line in text.split("\n"):
        if any(k in line.lower() for k in ["explanation", "solution", "bugs"]):
            break
        cleaned.append(line)

    return "\n".join(cleaned).strip()


# ---------------- CORE ----------------
def generate_fixed_code(code):
    prompt = f"""
You are a Python security expert.

Fix the given code safely.

STRICT RULES:
- No eval
- No exec
- No os.system
- No subprocess execution of user input
- No pickle.loads
- Do not execute user input

IMPORTANT:
- Keep the program runnable
- Replace unsafe code with safe alternatives (print statements if needed)
- Do NOT leave broken syntax

Return ONLY Python code.

CODE:
{code}
"""

    raw = ask_llm(prompt)
    cleaned = extract_code_only(raw)
    safe = sanitize_code(cleaned)

    return safe


# ---------------- TERMINAL ----------------
def main():
    print("🚀 AI Code Fixer Terminal")
    print("Paste your Python code below.")
    print("Type 'RUN' to process, 'exit' to quit.\n")

    while True:
        lines = []

        while True:
            line = input(">>> ")

            if line.lower() == "exit":
                return

            if line == "RUN":
                break

            lines.append(line)

        user_code = "\n".join(lines)

        print("\n🔍 Processing...\n")

        result = generate_fixed_code(user_code)

        print("===== FIXED CODE =====\n")
        print(result)
        print("\n=======================\n")


if __name__ == "__main__":
    main()