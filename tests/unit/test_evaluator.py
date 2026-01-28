"""Unit tests for the evaluator module."""

from unittest.mock import AsyncMock

import pytest

from src.evaluation.evaluator import evaluate
from src.models.scan_result import EmailEvaluation, EvaluationResult, ScanResult
from src.models.signal import Signal


class TestEvaluator:
    """Unit tests for the evaluation module."""

    async def test_evaluate_computes_metrics_correctly(self):
        """T029: Test evaluate() computes recall, precision, f1 correctly."""
        # Create mock scanner that returns predefined results
        mock_scanner = AsyncMock()

        # Mock scan results for 3 example emails
        mock_scanner.scan.side_effect = [
            ScanResult(
                risk_score=20,
                classification="Safe",
                explanation="Safe email",
                signals=[Signal("url_count", "URL Count", 0, -0.1)],
                llm_escalated=False
            ),  # Predicted: Safe, Actual: Safe (correct)
            ScanResult(
                risk_score=80,
                classification="Phishing",
                explanation="Phishing email",
                signals=[Signal("urgency_keyword_count", "Urgency Keywords", 5, 0.8)],
                llm_escalated=True
            ),  # Predicted: Phishing, Actual: Phishing (correct)
            ScanResult(
                risk_score=60,
                classification="Suspicious",
                explanation="Borderline email",
                signals=[Signal("has_suspicious_url", "Suspicious URL", True, 0.5)],
                llm_escalated=True
            )  # Predicted: Suspicious, Actual: Phishing (incorrect - false negative)
        ]

        # Example emails with known labels
        examples = [
            {"id": "safe-001", "email_text": "hi", "sender": "sender", "label": "Safe"},
            {"id": "phishing-001", "email_text": "urgent", "sender": "sender", "label": "Phishing"},
            {"id": "phishing-002", "email_text": "click here", "sender": "sender", "label": "Phishing"},
        ]

        # Run evaluation
        result = await evaluate(mock_scanner, examples)

        # Verify result structure
        assert isinstance(result, EvaluationResult)
        assert isinstance(result.recall, float)
        assert isinstance(result.precision, float)
        assert isinstance(result.f1, float)
        assert isinstance(result.per_email, list)
        assert len(result.per_email) >= 3

        # Verify per-email results
        for email_result in result.per_email:
            assert isinstance(email_result, EmailEvaluation)
            assert hasattr(email_result, 'email_id')
            assert hasattr(email_result, 'predicted')
            assert hasattr(email_result, 'actual')
            assert hasattr(email_result, 'risk_score')
            assert hasattr(email_result, 'correct')
            assert hasattr(email_result, 'signals')

    async def test_evaluate_handles_false_negatives(self):
        """T029: Test false negative flagging in evaluation."""
        mock_scanner = AsyncMock()

        # Return a result that's a false negative (predicted Safe, actual Phishing)
        mock_scanner.scan.return_value = ScanResult(
            risk_score=30,
            classification="Safe",
            explanation="Looks safe",
            signals=[Signal("url_count", "URL Count", 1, -0.2)],
            llm_escalated=False
        )

        examples = [
            {"id": "fn-001", "email_text": "urgent", "sender": "sender", "label": "Phishing"}
        ]

        result = await evaluate(mock_scanner, examples)

        # Verify the false negative is marked correctly
        assert len(result.per_email) == 1
        fn_result = result.per_email[0]
        assert fn_result.actual == "Phishing"
        assert fn_result.predicted == "Safe"
        assert fn_result.correct is False  # This is a false negative

    async def test_evaluate_metrics_range(self):
        """T029: Test that metrics are in [0,1] range."""
        mock_scanner = AsyncMock()
        mock_scanner.scan.return_value = ScanResult(
            risk_score=50,
            classification="Suspicious",
            explanation="Suspicious",
            signals=[Signal("urgency_keyword_count", "Urgency Keywords", 2, 0.3)],
            llm_escalated=True
        )

        examples = [
            {"id": "test-001", "email_text": "test", "sender": "sender", "label": "Suspicious"}
        ]

        result = await evaluate(mock_scanner, examples)

        # Verify metrics are in [0,1] range
        assert 0.0 <= result.recall <= 1.0
        assert 0.0 <= result.precision <= 1.0
        assert 0.0 <= result.f1 <= 1.0

    async def test_evaluate_per_email_results_detailed(self):
        """T029: Test per-email results contain all expected fields."""
        mock_scanner = AsyncMock()
        signals = [
            Signal("urgency_keyword_count", "Urgency Keywords", 3, 0.8),
            Signal("has_suspicious_url", "Suspicious URL", True, 0.6)
        ]
        mock_scanner.scan.return_value = ScanResult(
            risk_score=75,
            classification="Phishing",
            explanation="Phishing detected",
            signals=signals,
            llm_escalated=True
        )

        examples = [
            {"id": "detailed-001", "email_text": "urgent phishing", "sender": "fake", "label": "Phishing"}
        ]

        result = await evaluate(mock_scanner, examples)

        assert len(result.per_email) == 1
        email_result = result.per_email[0]

        # Check all expected fields are present
        assert email_result.email_id == "detailed-001"
        assert email_result.predicted == "Phishing"
        assert email_result.actual == "Phishing"
        assert email_result.risk_score == 75
        assert email_result.correct is True
        assert len(email_result.signals) >= 2