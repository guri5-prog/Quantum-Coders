import subprocess

def run_safe(code):
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            timeout=2,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Execution timed out (Possible DoS)"