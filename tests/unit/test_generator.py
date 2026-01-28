"""Unit tests for explanation generator module."""

import pytest

from src.explanation.generator import generate_explanation
from src.models.signal import Signal
from src.models.scan_result import LLMReviewResult


JARGON_DENY_LIST = [
    "coefficient", "logistic regression", "predict_proba", "vectorizer",
    "sklearn", "scikit", "numpy", "feature importance", "model weight",
    "hyperparameter", "regularization", "epoch", "gradient",
]


class TestGenerateExplanation:
    """Tests for generate_explanation() per contract scanner-api.md §5."""

    def test_safe_explanation_contains_verdict(self, sample_signals):
        explanation = generate_explanation("Safe", sample_signals, risk_score=15)
        assert "Final Verdict: Safe" in explanation

    def test_phishing_explanation_references_signals(self, sample_signals):
        explanation = generate_explanation("Phishing", sample_signals, risk_score=85)
        # Should reference at least one signal template output
        assert "ML Analysis:" in explanation
        assert "\u2022" in explanation  # bullet points

    def test_explanation_contains_verdict_reasoning_next_steps(self, sample_signals):
        explanation = generate_explanation("Phishing", sample_signals, risk_score=85)
        # Must have: Final Verdict, Risk Score, ML Analysis, User Guidance
        assert "Final Verdict:" in explanation
        assert "Risk Score:" in explanation
        assert "ML Analysis:" in explanation
        assert "User Guidance:" in explanation
        lines = [line for line in explanation.split("\n") if line.strip()]
        assert len(lines) >= 3

    def test_no_technical_jargon(self, sample_signals):
        explanation = generate_explanation("Phishing", sample_signals, risk_score=85)
        for jargon in JARGON_DENY_LIST:
            assert jargon.lower() not in explanation.lower(), (
                f"Explanation contains technical jargon: '{jargon}'"
            )

    def test_without_llm_output(self, sample_signals):
        explanation = generate_explanation("Suspicious", sample_signals, risk_score=55, llm_output=None)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "LLM Review:" not in explanation

    def test_with_llm_output(self, sample_signals):
        llm_result = LLMReviewResult(
            llm_explanation="This email shows signs of social engineering targeting financial data.",
            suggested_label=None,
            rationale="Based on urgency keyword count and suspicious URLs.",
            prompt_log="test prompt",
            response_log="test response",
        )
        explanation = generate_explanation("Suspicious", sample_signals, risk_score=55, llm_output=llm_result)
        assert "social engineering" in explanation.lower()
        assert "LLM Review:" in explanation

    def test_safe_email_explanation(self):
        signals = [
            Signal(name="urgency_keyword_count", display_name="Urgent language", value=0, weight=-0.3),
            Signal(name="url_count", display_name="Links found", value=0, weight=-0.2),
            Signal(name="has_attachment_reference", display_name="Attachment reference", value=True, weight=-0.1),
        ]
        explanation = generate_explanation("Safe", signals, risk_score=10)
        assert "Final Verdict: Safe" in explanation
        assert "Risk Score: 10%" in explanation
