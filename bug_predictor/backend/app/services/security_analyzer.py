import json
import os
import subprocess
import sys
import tempfile

from ..utils.language_analysis import (
    detect_generic_security,
    has_python_ast_support,
    language_extension,
)

def analyze_security(code: str, language="python"):
    if not has_python_ast_support(language):
        return detect_generic_security(code, language)

    with tempfile.NamedTemporaryFile(delete=False, suffix=language_extension(language)) as f:
        f.write(code.encode())
        filename = f.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", "-r", filename],
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            return []

        report = json.loads(result.stdout)
        return [
            {
                "type": issue.get("test_name"),
                "severity": issue.get("issue_severity"),
                "confidence": issue.get("issue_confidence"),
                "message": issue.get("issue_text"),
                "line": issue.get("line_number")
            }
            for issue in report.get("results", [])
        ]
    except (json.JSONDecodeError, FileNotFoundError, OSError) as exc:
        return [{"type": "tool_error", "message": str(exc)}]
    finally:
        if os.path.exists(filename):
            os.unlink(filename)
