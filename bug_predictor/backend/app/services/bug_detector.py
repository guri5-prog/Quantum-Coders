import subprocess
import tempfile

def detect_bugs(code: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        filename = f.name

    result = subprocess.run(
        ["pylint", filename, "--disable=all", "--enable=E,W"],
        capture_output=True,
        text=True
    )

    return result.stdout.split("\n")