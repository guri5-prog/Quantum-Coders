import subprocess
import tempfile

def debug_code(code: str):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode())
            filename = f.name

        result = subprocess.run(
            ["python", filename],
            capture_output=True,
            text=True,
            timeout=2   
        )

        return {
            "status": "success",
            "output": result.stdout
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Execution timed out (Possible DoS attack)"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }