import os
import subprocess
import tempfile


def debug_code(code: str):
    filename = None

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

        if result.returncode != 0:
            return {
                "status": "error",
                "message": result.stderr.strip() or "Code execution failed",
                "output": result.stdout
            }

        return {
            "status": "success",
            "output": result.stdout
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Execution timed out (Possible DoS attack)"
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc)
        }
    finally:
        if filename and os.path.exists(filename):
            os.unlink(filename)
