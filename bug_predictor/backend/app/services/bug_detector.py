import json
import os
import subprocess
import tempfile


def detect_bugs(code: str):
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        filename = f.name

    try:
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            backend_root
            if not existing_pythonpath
            else os.pathsep.join([backend_root, existing_pythonpath])
        )

        result = subprocess.run(
            ["pylint", filename, "--disable=all", "--enable=E,W", "--output-format=json"],
            capture_output=True,
            text=True,
            cwd=backend_root,
            env=env
        )

        if not result.stdout.strip():
            return []

        messages = json.loads(result.stdout)
        return [
            {
                "type": message.get("type"),
                "symbol": message.get("symbol"),
                "message": message.get("message"),
                "line": message.get("line"),
                "column": message.get("column")
            }
            for message in messages
        ]
    except (json.JSONDecodeError, FileNotFoundError, OSError) as exc:
        return [{"type": "tool_error", "message": str(exc)}]
    finally:
        if os.path.exists(filename):
            os.unlink(filename)
