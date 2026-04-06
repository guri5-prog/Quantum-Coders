from fastapi import APIRouter

from ..services.anomaly_detector import detect_anomalies
from ..services.bug_detector import detect_bugs
from ..services.code_fixer import generate_fixed_code
from ..services.debugger import debug_code
from ..services.dos_detector import detect_dos
from ..services.risk_calculator import calculate_risk
from ..services.security_analyzer import analyze_security
from ..utils.language_analysis import normalize_language

router = APIRouter()


@router.post("/analyze")
def analyze_code(payload: dict):
    if "code" in payload:
        codes = [payload["code"]]
        languages = [normalize_language(payload.get("language", "python"))]
    elif "codes" in payload:
        codes = payload["codes"]
        payload_languages = payload.get("languages")
        if isinstance(payload_languages, list) and len(payload_languages) == len(codes):
            languages = [normalize_language(item) for item in payload_languages]
        else:
            default_language = normalize_language(payload.get("language", "python"))
            languages = [default_language] * len(codes)
    else:
        return {"error": "Provide 'code' or 'codes'"}

    results = []

    for code, language in zip(codes, languages):
        bugs = detect_bugs(code, language)
        security = analyze_security(code, language)
        anomalies = detect_anomalies(code, language)
        dos_risk = detect_dos(code, language)
        debug_result = debug_code(code, language)
        risk = calculate_risk(bugs, security, anomalies, dos_risk, code, language)
        fixed_code = generate_fixed_code(code, bugs, security, language)

        results.append({
            "input_code": code,
            "language": language,
            "bugs": bugs,
            "security": security,
            "anomalies": anomalies,
            "dos_risk": dos_risk,
            "debug": debug_result,
            "fixed_code": fixed_code,
            "risk": risk
        })

    return {
        "total_inputs": len(results),
        "results": results
    }
