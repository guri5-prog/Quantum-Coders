from fastapi import APIRouter

from ..services.anomaly_detector import detect_anomalies
from ..services.bug_detector import detect_bugs
from ..services.debugger import debug_code
from ..services.dos_detector import detect_dos
from ..services.risk_calculator import calculate_risk
from ..services.security_analyzer import analyze_security

router = APIRouter()


@router.post("/analyze")
def analyze_code(payload: dict):
    if "code" in payload:
        codes = [payload["code"]]
    elif "codes" in payload:
        codes = payload["codes"]
    else:
        return {"error": "Provide 'code' or 'codes'"}

    results = []

    for code in codes:
        bugs = detect_bugs(code)
        security = analyze_security(code)
        anomalies = detect_anomalies(code)
        dos_risk = detect_dos(code)
        debug_result = debug_code(code)
        risk = calculate_risk(bugs, security, anomalies, dos_risk, code)

        results.append({
            "input_code": code,
            "bugs": bugs,
            "security": security,
            "anomalies": anomalies,
            "dos_risk": dos_risk,
            "debug": debug_result,
            "risk": risk
        })

    return {
        "total_inputs": len(results),
        "results": results
    }
