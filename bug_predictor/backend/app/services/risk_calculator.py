def calculate_risk(bugs, security, anomalies, dos, code):

    from app.utils.parser import analyze_ast

    ast_result = analyze_ast(code)
    features = ast_result.get("features", {})

    score = 0
    reasons = []

    # -------------------------------
    # 🔐 1. SECURITY ISSUES (HIGH PRIORITY)
    # -------------------------------
    if len(security) > 0:
        score += 0.5
        reasons.append("Security vulnerabilities detected")

    # -------------------------------
    # 🧠 2. ANOMALY SEVERITY-BASED SCORING
    # -------------------------------
    for issue in anomalies:
        severity = issue.get("severity", "LOW")

        if severity == "HIGH":
            score += 0.5
        elif severity == "MEDIUM":
            score += 0.3
        else:
            score += 0.1

    if len(anomalies) > 0:
        reasons.append("Unsafe coding patterns found")

    # -------------------------------
    # 💥 3. DOS RISK (CRITICAL)
    # -------------------------------
    if len(dos) > 0:
        score = max(score, 0.85)   # 🔥 force HIGH risk

    # -------------------------------
    # 🧬 4. CODE COMPLEXITY
    # -------------------------------
    complexity_score = (
        features.get("functions", 0) * 0.05 +
        features.get("loops", 0) * 0.1 +
        features.get("assignments", 0) * 0.02
    )

    score += complexity_score

    if complexity_score > 0.3:
        reasons.append("High code complexity")

    # -------------------------------
    # 🐞 5. BUGS (LOW IMPACT)
    # -------------------------------
    score += len(bugs) * 0.1

    # -------------------------------
    # 🔒 NORMALIZE SCORE
    # -------------------------------
    score = min(score, 1.0)

    # -------------------------------
    # 🎯 RISK LEVEL CLASSIFICATION
    # -------------------------------
    if score >= 0.75:
        level = "HIGH"
        color = "RED"
    elif score >= 0.4:
        level = "MEDIUM"
        color = "ORANGE"
    else:
        level = "LOW"
        color = "GREEN"

    # -------------------------------
    # 🧠 ADD SMART EXPLANATION
    # -------------------------------
    if not reasons:
        reasons.append("No major risks detected")

    return {
        "score": round(score, 2),
        "percentage": int(score * 100),
        "level": level,
        "color": color,
        "reasons": reasons,
        "features": features
    }