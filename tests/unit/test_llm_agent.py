"""Unit tests for LLM escalation module."""

import pytest
from unittest.mock import patch, AsyncMock

from src.models.scan_result import LLMReviewResult, ScanResult
from src.models.signal import Signal


class TestLLMEscalation:
    """Unit tests for the LLM escalation agent."""

    async def test_escalate_triggers_for_borderline_scores(self):
        """T024: Test LLM escalation for borderline scores (45-70)."""
        from src.escalation.llm_agent import escalate

        # Mock the agents framework and LLM call to avoid external dependency during tests
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'mock_api_key'}):
            with patch('agents.run.Runner.run') as mock_run:
                # Create mock result
                mock_result = AsyncMock()
                mock_result.final_output = "This email appears to be suspicious based on the sender mismatch and urgency language."
                mock_run.return_value = mock_result

                # Test borderline score (50)
                result = await escalate(
                    email_text="Urgent: Update your account now!",
                    sender="suspicious@example.com",
                    risk_score=50,
                    classification="Suspicious",
                    signals=[Signal("urgency_keyword_count", "Urgency Keywords", 2, 0.8)]
                )

                assert isinstance(result, LLMReviewResult)
                assert "suspicious" in result.llm_explanation.lower()
                assert result.prompt_log and len(result.prompt_log) > 0
                assert result.response_log and len(result.response_log) > 0

    async def test_escalate_triggers_for_high_impact_context(self):
        """T024: Test LLM escalation for high-impact contexts (finance/HR/executive)."""
        from src.escalation.llm_agent import escalate

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'mock_api_key'}):
            with patch('agents.run.Runner.run') as mock_run:
                # Create mock result
                mock_result = AsyncMock()
                mock_result.final_output = "This HR-related email requires careful review."
                mock_run.return_value = mock_result

                # Test safe score but high-impact context
                result = await escalate(
                    email_text="HR: Update your payroll information immediately.",
                    sender="hr@company.com",
                    risk_score=30,
                    classification="Safe",
                    signals=[Signal("is_high_impact_context", "High-Impact Context", True, 0.5)]
                )

                assert isinstance(result, LLMReviewResult)
                assert "hr" in result.llm_explanation.lower()

    async def test_integration_escalation_triggers_correctly(self):
        """T025: Integration test for LLM escalation pipeline behavior."""
        from src.config import ScannerConfig
        from src.pipeline.scanner import EmailScanner
        from src.escalation.llm_agent import escalate as real_escalate

        config = ScannerConfig(llm_enabled=True)
        scanner = EmailScanner(config)

        # Mock the actual escalate function to return a controlled response
        with patch('src.escalation.llm_agent.escalate') as mock_escalate:
            mock_escalate.return_value = LLMReviewResult(
                llm_explanation="Mock LLM review",
                suggested_label="Phishing",
                rationale="Based on suspicious URL",
                prompt_log="mock prompt",
                response_log="mock response"
            )

            # Test with email that has high-impact context to guarantee escalation
            result = await scanner.scan(
                "Dear employee, please confirm your payroll and salary details by clicking the link below.",
                "hr@company.com"
            )

            assert result.llm_escalated is True
            assert result.llm_output is not None
            assert "mock" in result.llm_output.llm_explanation.lower()

    async def test_integration_escalation_disabled(self):
        """T025: Integration test for disabled LLM escalation."""
        from src.config import ScannerConfig
        from src.pipeline.scanner import EmailScanner

        config = ScannerConfig(llm_enabled=False)
        scanner = EmailScanner(config)

        # Test that even borderline emails don't escalate when disabled
        result = await scanner.scan(
            "Please verify your account at suspicious-domain.com",
            "fake@bank.com"
        )

        assert result.llm_escalated is False
        assert result.llm_output is None

    async def test_integration_escalation_fallback_on_error(self):
        """T025: Integration test for LLM fallback when service unavailable."""
        from src.config import ScannerConfig
        from src.pipeline.scanner import EmailScanner

        config = ScannerConfig(llm_enabled=True)
        scanner = EmailScanner(config)

        # Mock LLM to raise exception
        with patch('src.pipeline.scanner.EmailScanner._try_escalate') as mock_escalate:
            mock_escalate.return_value = (False, None)  # Fallback behavior

            result = await scanner.scan(
                "Please verify your account at suspicious-domain.com",
                "fake@bank.com"
            )

            assert result.llm_escalated is False
            assert result.llm_output is None
            # Should still have ML-only result
            assert result.risk_score > 0
            assert result.classification in ("Safe", "Suspicious", "Phishing")
