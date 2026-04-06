from ..utils.parser import analyze_ast

def detect_anomalies(code: str):
    result = analyze_ast(code)

    if "error" in result:
        return [{"message": "Parsing failed"}]

    return result["issues"]
