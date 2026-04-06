from ..utils.language_analysis import (
    extract_generic_features,
    has_python_ast_support,
    normalize_language,
)


def calculate_risk(bugs, security, anomalies, dos, code, language="python"):
    if has_python_ast_support(language):
        from ..utils.parser import analyze_ast
        ast_result = analyze_ast(code)
        features = ast_result.get("features", {})
    else:
        features = extract_generic_features(code)

    score = 0.0
    reasons = []

    bug_count = sum(1 for issue in bugs if issue.get("type") != "tool_error")
    security_count = sum(1 for issue in security if issue.get("type") != "tool_error")
    anomaly_count = len(anomalies)
    dos_count = len(dos)
    has_findings = any([bug_count, security_count, anomaly_count, dos_count])
    critical_security_count = 0
    high_severity_security_count = 0

    for issue in security:
        if not isinstance(issue, dict) or issue.get("type") == "tool_error":
            continue

        issue_type = str(issue.get("type", "")).lower()
        issue_message = str(issue.get("message", "")).lower()
        issue_severity = str(issue.get("severity", "")).upper()

        if issue_severity in {"HIGH", "CRITICAL"}:
            high_severity_security_count += 1

        if (
            "command" in issue_type
            or "command" in issue_message
            or "sql" in issue_type
            or "sql" in issue_message
            or "eval" in issue_type
            or "eval" in issue_message
            or "unsafe_c_api" in issue_type
        ):
            critical_security_count += 1

    if security_count > 0:
        score += 0.35
        reasons.append("Security vulnerabilities detected")

    if high_severity_security_count > 0:
        score += min(0.18 * high_severity_security_count, 0.35)
        reasons.append("High-severity security issues found")

    if critical_security_count > 0:
        score = max(score, 0.78)
        reasons.append("Critical injection or command-execution risk detected")

    for issue in anomalies:
        severity = issue.get("severity", "LOW")

        if severity == "HIGH":
            score += 0.18
        elif severity == "MEDIUM":
            score += 0.1
        else:
            score += 0.04

    if anomalies:
        reasons.append("Unsafe coding patterns found")

    if dos_count > 0:
        score = max(score, 0.9)
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

    score += min(bug_count * 0.05, 0.2)

    if bug_count > 0:
        reasons.append("Static analysis warnings found")

    if any(isinstance(issue, dict) and issue.get("type") == "tool_error" for issue in bugs + security):
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
        "features": features,
        "language": normalize_language(language),
    }
