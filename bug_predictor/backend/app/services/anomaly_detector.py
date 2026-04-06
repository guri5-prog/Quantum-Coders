from ..utils.parser import analyze_ast
from ..utils.language_analysis import detect_generic_anomalies, has_python_ast_support

def detect_anomalies(code: str, language="python"):
    if not has_python_ast_support(language):
        return detect_generic_anomalies(code, language)

    result = analyze_ast(code)

    if "error" in result:
        return [{"message": "Parsing failed"}]

    return result["issues"]
