from fastapi import APIRouter
from app.services.bug_detector import detect_bugs
from app.services.security_analyzer import analyze_security
from app.services.anomaly_detector import detect_anomalies
from app.services.dos_detector import detect_dos
from app.services.risk_calculator import calculate_risk
from app.services.debugger import debug_code

router = APIRouter()

@router.post("/analyze")
def analyze_code(payload: dict):
    
    # ✅ Support BOTH single and multiple inputs
    if "code" in payload:
        codes = [payload["code"]]   # convert single → list
    elif "codes" in payload:
        codes = payload["codes"]
    else:
        return {"error": "Provide 'code' or 'codes'"}

    results = []

    for code in codes:
        bugs = []
        security = []

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

    # ✅ Return clean response
    return {
        "total_inputs": len(results),
        "results": results
    }