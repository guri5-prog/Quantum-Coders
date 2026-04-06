import subprocess
import tempfile

def analyze_security(code: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        filename = f.name

    result = subprocess.run(
        ["bandit", "-r", filename],
        capture_output=True,
        text=True
    )

    return result.stdout.split("\n")