def calculate_risk(bugs, security, anomalies, dos, code):
    from ..utils.parser import analyze_ast

    ast_result = analyze_ast(code)
    features = ast_result.get("features", {})

    score = 0
    reasons = []

    bug_count = sum(1 for issue in bugs if issue.get("type") != "tool_error")
    security_count = sum(1 for issue in security if issue.get("type") != "tool_error")
    anomaly_count = len(anomalies)
    dos_count = len(dos)
    has_findings = any([bug_count, security_count, anomaly_count, dos_count])

    if security_count > 0:
        score += 0.5
        reasons.append("Security vulnerabilities detected")

    for issue in anomalies:
        severity = issue.get("severity", "LOW")

        if severity == "HIGH":
            score += 0.5
        elif severity == "MEDIUM":
            score += 0.3
        else:
            score += 0.1

    if anomalies:
        reasons.append("Unsafe coding patterns found")

    if dos_count > 0:
        score = max(score, 0.85)
        reasons.append("Potential denial-of-service pattern detected")

    complexity_score = (
        features.get("functions", 0) * 0.05 +
        features.get("loops", 0) * 0.1 +
        features.get("assignments", 0) * 0.02
    )

    if has_findings:
        complexity_impact = min(complexity_score * 0.25, 0.15)
        score += complexity_impact

        if complexity_score > 0.6:
            reasons.append("High code complexity may increase maintenance risk")

    score += min(bug_count * 0.1, 0.3)

    if bug_count > 0:
        reasons.append("Static analysis warnings found")

    if any(issue.get("type") == "tool_error" for issue in bugs + security):
        reasons.append("One or more analysis tools could not complete")

    score = min(score, 1.0)

    if not has_findings:
        score = min(score, 0.25)

    if score >= 0.75:
        level = "HIGH"
        color = "RED"
    elif score >= 0.4:
        level = "MEDIUM"
        color = "ORANGE"
    else:
        level = "LOW"
        color = "GREEN"

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
