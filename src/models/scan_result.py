"""Scan result and LLM review data structures."""

from dataclasses import dataclass, field

from src.models.signal import Signal


@dataclass
class LLMReviewResult:
    """Output from the LLM escalation agent.

    Attributes:
        llm_explanation: LLM-generated reasoning summary.
        suggested_label: Optional refined verdict label.
        rationale: Justification referencing ML signals.
        prompt_log: Full prompt sent to LLM (for auditability).
        response_log: Full LLM response (for auditability).
    """

    llm_explanation: str
    suggested_label: str | None
    rationale: str
    prompt_log: str
    response_log: str


@dataclass
class ScanResult:
    """The complete output of scanning a single email.

    Attributes:
        risk_score: Phishing confidence score (0-100).
        classification: One of "Safe", "Suspicious", "Phishing".
        explanation: Plain-English explanation.
        signals: Top contributing signals from ML classifier.
        llm_escalated: Whether LLM review was triggered.
        llm_output: LLM review output if escalated, else None.
    """

    risk_score: int
    classification: str
    explanation: str
    signals: list[Signal] = field(default_factory=list)
    llm_escalated: bool = False
    llm_output: LLMReviewResult | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.risk_score <= 100:
            raise ValueError(f"risk_score must be 0-100, got {self.risk_score}")
        if self.classification not in ("Safe", "Suspicious", "Phishing"):
            raise ValueError(f"classification must be Safe/Suspicious/Phishing, got {self.classification}")


@dataclass
class EmailEvaluation:
    """Per-email evaluation detail."""

    email_id: str
    predicted: str
    actual: str
    risk_score: int
    correct: bool
    signals: list[Signal] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Aggregate output from evaluation against labeled examples."""

    recall: float
    precision: float
    f1: float
    per_email: list[EmailEvaluation] = field(default_factory=list)
