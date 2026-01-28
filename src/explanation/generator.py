"""Plain-English explanation builder from signals and optional LLM output.

Per contract scanner-api.md §5 and research.md R5.
"""

from src.models.scan_result import LLMReviewResult
from src.models.signal import Signal

# Signal-to-English templates per research.md R5
_SIGNAL_TEMPLATES: dict[str, str] = {
    "urgency_keyword_count": "High urgency phrases detected ({value} found)",
    "url_count": "Multiple embedded links ({value} found)",
    "has_suspicious_url": "Suspicious or unfamiliar URLs detected",
    "sender_domain_mismatch": "External sender with domain mismatch",
    "financial_keyword_count": "Financial keywords detected ({value} found)",
    "has_attachment_reference": "Attachment reference detected",
    "is_high_impact_context": "High-impact context (financial, HR, or executive)",
    "executive_keyword_count": "Executive-level terminology detected ({value} found)",
    "hr_keyword_count": "HR-related topics detected ({value} found)",
}

_USER_GUIDANCE: dict[str, str] = {
    "Safe": "No immediate action is needed. This email appears legitimate.",
    "Suspicious": (
        "Exercise caution with this email.\n"
        "Avoid clicking links or downloading attachments until you verify the sender.\n"
        "Report to IT/security if uncertain."
    ),
    "Phishing": (
        "Do not click any links or provide information.\n"
        "Report this email to IT/security.\n"
        "Delete the email after reporting."
    ),
}


def generate_explanation(
    classification: str,
    signals: list[Signal],
    risk_score: int = 0,
    llm_output: LLMReviewResult | None = None,
) -> str:
    """Build a plain-English explanation from signals and optional LLM output.

    The explanation answers:
    1. What is the final verdict?
    2. What is the risk score?
    3. What did the ML analysis find?
    4. What did the LLM review find (if escalated)?
    5. What should the user do next?

    Args:
        classification: "Safe", "Suspicious", or "Phishing".
        signals: Top contributing signals with human-readable names.
        risk_score: ML-produced risk score (0-100).
        llm_output: Optional LLM review result for enhanced reasoning.

    Returns:
        Plain-English string with no technical jargon.
    """
    parts: list[str] = []

    # 1. Final Verdict
    parts.append(f"Final Verdict: {classification}")
    parts.append(f"Risk Score: {risk_score}%")
    parts.append("")

    # 2. ML Analysis - signal explanations
    parts.append("ML Analysis:")
    relevant_signals = _get_relevant_signals(signals, classification)
    if relevant_signals:
        for signal in relevant_signals:
            explanation = _format_signal(signal)
            if explanation:
                parts.append(f"  \u2022 {explanation}")
    else:
        parts.append("  \u2022 No significant warning signals were detected.")
    parts.append("")

    # 3. LLM Review (if available)
    if llm_output is not None:
        parts.append("LLM Review:")
        parts.append(llm_output.llm_explanation)
        if llm_output.suggested_label and llm_output.suggested_label != classification:
            parts.append(
                f"Note: LLM analysis suggests this may be classified as "
                f"{llm_output.suggested_label}. {llm_output.rationale}"
            )
        parts.append("")

    # 4. User Guidance
    guidance = _USER_GUIDANCE.get(classification, "Review this email carefully.")
    parts.append("User Guidance:")
    parts.append(guidance)

    return "\n".join(parts)


def _get_relevant_signals(signals: list[Signal], classification: str) -> list[Signal]:
    """Filter signals to show the most relevant ones for the classification."""
    if classification == "Safe":
        # For safe emails, show positive signals (low risk indicators)
        return [s for s in signals[:5] if _is_noteworthy(s)]
    else:
        # For suspicious/phishing, show high-weight negative signals
        return [s for s in signals[:5] if _is_concerning(s)]


def _is_noteworthy(signal: Signal) -> bool:
    """Check if a signal is worth mentioning for safe emails."""
    if signal.name == "has_attachment_reference" and signal.value:
        return True
    if signal.name in ("urgency_keyword_count", "url_count") and signal.value == 0:
        return True
    return signal.weight != 0


def _is_concerning(signal: Signal) -> bool:
    """Check if a signal indicates concern."""
    if isinstance(signal.value, bool):
        return signal.value is True
    if isinstance(signal.value, (int, float)):
        return signal.value > 0
    return True


def _format_signal(signal: Signal) -> str | None:
    """Format a signal into a plain-English bullet point."""
    template = _SIGNAL_TEMPLATES.get(signal.name)
    if template:
        if isinstance(signal.value, bool):
            if signal.value:
                return template
            return None
        return template.format(value=signal.value)
    # Fallback for unknown signals
    return f"{signal.display_name}: {signal.value}"
