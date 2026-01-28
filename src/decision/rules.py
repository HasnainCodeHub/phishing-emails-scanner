"""Rule-based classification using deterministic thresholds.

Per contract scanner-api.md §3.
"""


def classify(
    risk_score: int,
    features: dict[str, float | int | bool],
    safe_threshold: int = 45,
    phishing_threshold: int = 70,
) -> tuple[str, bool, bool]:
    """Apply rule-based thresholds to determine classification.

    Boundary rules:
        - score < safe_threshold -> "Safe"
        - score > phishing_threshold -> "Phishing"
        - safe_threshold <= score <= phishing_threshold -> "Suspicious"

    Args:
        risk_score: ML-produced score (0-100).
        features: Named feature dictionary (used for high-impact detection).
        safe_threshold: Scores below this are "Safe" (default 45).
        phishing_threshold: Scores above this are "Phishing" (default 70).

    Returns:
        Tuple of (classification, is_borderline, is_high_impact).
    """
    if risk_score < safe_threshold:
        classification = "Safe"
    elif risk_score > phishing_threshold:
        classification = "Phishing"
    else:
        classification = "Suspicious"

    is_borderline = safe_threshold <= risk_score <= phishing_threshold
    is_high_impact = bool(features.get("is_high_impact_context", False))

    return classification, is_borderline, is_high_impact
