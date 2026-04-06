from fastapi import APIRouter

from ..services.anomaly_detector import detect_anomalies
from ..services.bug_detector import detect_bugs
from ..services.code_fixer import generate_fixed_code
from ..services.debugger import debug_code
from ..services.dos_detector import detect_dos
from ..services.risk_calculator import calculate_risk
from ..services.security_analyzer import analyze_security
from ..utils.language_analysis import detect_mixed_language, normalize_language

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
        effective_language, language_signals = detect_mixed_language(code, language)

        bugs = detect_bugs(code, effective_language)
        security = analyze_security(code, effective_language)
        anomalies = detect_anomalies(code, effective_language)
        dos_risk = detect_dos(code, effective_language)
        debug_result = debug_code(code, effective_language)
        risk = calculate_risk(bugs, security, anomalies, dos_risk, code, effective_language)
        fixed_code = generate_fixed_code(code, bugs, security, effective_language)

        analysis_notes = []
        if effective_language == "mixed":
            analysis_notes.append(
                "Detected mixed-language syntax in one submission. Results are heuristic and may be less precise."
            )
            anomalies.append({
                "type": "Mixed Language Input",
                "message": "Multiple language signatures detected. Analyze one language per submission for highest accuracy.",
                "severity": "MEDIUM",
            })

        results.append({
            "input_code": code,
            "language": effective_language,
            "requested_language": language,
            "language_signals": language_signals,
            "analysis_notes": analysis_notes,
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
