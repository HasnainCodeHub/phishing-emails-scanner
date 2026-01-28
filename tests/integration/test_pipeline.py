"""Integration tests for ML-only pipeline (no LLM)."""

import os
import tempfile

import pytest

from src.config import ScannerConfig
from src.models.scan_result import ScanResult
from src.pipeline.scanner import EmailScanner
from src.scoring.classifier import PhishingClassifier


@pytest.fixture
def scanner_config():
    """Create a scanner config with a trained model."""
    training_data = [
        {"urgency_keyword_count": 0, "url_count": 0, "has_suspicious_url": 0,
         "sender_domain_mismatch": 0, "financial_keyword_count": 0,
         "has_attachment_reference": 1, "is_high_impact_context": 0,
         "executive_keyword_count": 0, "hr_keyword_count": 0},
        {"urgency_keyword_count": 0, "url_count": 1, "has_suspicious_url": 0,
         "sender_domain_mismatch": 0, "financial_keyword_count": 0,
         "has_attachment_reference": 0, "is_high_impact_context": 0,
         "executive_keyword_count": 0, "hr_keyword_count": 0},
        {"urgency_keyword_count": 5, "url_count": 3, "has_suspicious_url": 1,
         "sender_domain_mismatch": 1, "financial_keyword_count": 2,
         "has_attachment_reference": 0, "is_high_impact_context": 1,
         "executive_keyword_count": 0, "hr_keyword_count": 0},
        {"urgency_keyword_count": 3, "url_count": 2, "has_suspicious_url": 1,
         "sender_domain_mismatch": 1, "financial_keyword_count": 1,
         "has_attachment_reference": 0, "is_high_impact_context": 1,
         "executive_keyword_count": 1, "hr_keyword_count": 0},
        {"urgency_keyword_count": 1, "url_count": 1, "has_suspicious_url": 0,
         "sender_domain_mismatch": 0, "financial_keyword_count": 1,
         "has_attachment_reference": 0, "is_high_impact_context": 1,
         "executive_keyword_count": 0, "hr_keyword_count": 1},
        {"urgency_keyword_count": 0, "url_count": 0, "has_suspicious_url": 0,
         "sender_domain_mismatch": 0, "financial_keyword_count": 0,
         "has_attachment_reference": 0, "is_high_impact_context": 0,
         "executive_keyword_count": 0, "hr_keyword_count": 0},
    ]
    labels = [0, 0, 1, 1, 0, 0]
    tmpdir = tempfile.mkdtemp()
    model_path = os.path.join(tmpdir, "test_model.joblib")
    PhishingClassifier.train(training_data, labels, model_path, seed=42)
    config = ScannerConfig(
        model_path=model_path,
        llm_enabled=False,
    )
    return config


@pytest.fixture
def scanner(scanner_config):
    return EmailScanner(scanner_config)


class TestPipelineMLOnly:
    """Integration tests for EmailScanner.scan() without LLM."""

    async def test_safe_email_scan(self, scanner, safe_email_text, safe_email_sender):
        result = await scanner.scan(safe_email_text, safe_email_sender)
        assert isinstance(result, ScanResult)
        assert 0 <= result.risk_score <= 100
        assert result.classification in ("Safe", "Suspicious", "Phishing")
        assert len(result.explanation) > 0
        assert len(result.signals) >= 3

    async def test_phishing_email_scan(self, scanner, phishing_email_text, phishing_email_sender):
        result = await scanner.scan(phishing_email_text, phishing_email_sender)
        assert isinstance(result, ScanResult)
        assert result.risk_score > 50
        assert result.classification in ("Suspicious", "Phishing")
        assert result.llm_escalated is False

    async def test_empty_email_raises_error(self, scanner):
        with pytest.raises(ValueError, match="empty"):
            await scanner.scan("", "sender@test.com")

    async def test_scan_result_has_all_fields(self, scanner, safe_email_text, safe_email_sender):
        result = await scanner.scan(safe_email_text, safe_email_sender)
        assert hasattr(result, "risk_score")
        assert hasattr(result, "classification")
        assert hasattr(result, "explanation")
        assert hasattr(result, "signals")
        assert hasattr(result, "llm_escalated")
        assert hasattr(result, "llm_output")

    async def test_llm_not_escalated_for_clear_cases(self, scanner, safe_email_text, safe_email_sender):
        result = await scanner.scan(safe_email_text, safe_email_sender)
        if result.risk_score < 45:
            assert result.llm_escalated is False
