import json
import os
import subprocess
import sys
import tempfile

from ..utils.language_analysis import (
    detect_generic_bugs,
    has_python_ast_support,
    language_extension,
)


def detect_bugs(code: str, language="python"):
    if not has_python_ast_support(language):
        return detect_generic_bugs(code, language)

    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    with tempfile.NamedTemporaryFile(delete=False, suffix=language_extension(language)) as f:
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
            [sys.executable, "-m", "pylint", filename, "--disable=all", "--enable=E,W", "--output-format=json"],
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
        fallback = detect_generic_bugs(code, language)
        if fallback:
            fallback.append({"type": "tool_error", "message": str(exc)})
            return fallback
        return [{"type": "tool_error", "message": str(exc)}]
    finally:
        if os.path.exists(filename):
            os.unlink(filename)
