"""Unit tests for feature extraction module."""

import pytest

from src.features.extractor import extract_features


class TestExtractFeatures:
    """Tests for extract_features() per contract scanner-api.md §1."""

    def test_safe_email_low_urgency(self, safe_email_text, safe_email_sender):
        features = extract_features(safe_email_text, safe_email_sender)
        assert isinstance(features, dict)
        assert features["urgency_keyword_count"] == 0
        assert features["has_suspicious_url"] is False

    def test_phishing_email_high_urgency(self, phishing_email_text, phishing_email_sender):
        features = extract_features(phishing_email_text, phishing_email_sender)
        assert features["urgency_keyword_count"] > 0
        assert features["url_count"] >= 2
        assert features["has_suspicious_url"] is True
        assert features["sender_domain_mismatch"] is True

    def test_output_is_dict_with_expected_keys(self, safe_email_text, safe_email_sender):
        features = extract_features(safe_email_text, safe_email_sender)
        expected_keys = {
            "urgency_keyword_count",
            "url_count",
            "has_suspicious_url",
            "sender_domain_mismatch",
            "financial_keyword_count",
            "has_attachment_reference",
            "is_high_impact_context",
            "executive_keyword_count",
            "hr_keyword_count",
        }
        assert set(features.keys()) == expected_keys

    def test_empty_email_raises_value_error(self):
        with pytest.raises(ValueError, match="empty"):
            extract_features("", "sender@example.com")

    def test_whitespace_only_email_raises_value_error(self):
        with pytest.raises(ValueError, match="empty"):
            extract_features("   \n\t  ", "sender@example.com")

    def test_missing_sender_still_extracts_features(self, safe_email_text):
        features = extract_features(safe_email_text, "")
        assert isinstance(features, dict)
        assert "urgency_keyword_count" in features

    def test_feature_values_are_correct_types(self, phishing_email_text, phishing_email_sender):
        features = extract_features(phishing_email_text, phishing_email_sender)
        assert isinstance(features["urgency_keyword_count"], int)
        assert isinstance(features["url_count"], int)
        assert isinstance(features["has_suspicious_url"], bool)
        assert isinstance(features["sender_domain_mismatch"], bool)
        assert isinstance(features["financial_keyword_count"], int)
        assert isinstance(features["has_attachment_reference"], bool)
        assert isinstance(features["is_high_impact_context"], bool)

    def test_borderline_email_has_hr_context(self, borderline_email_text, borderline_email_sender):
        features = extract_features(borderline_email_text, borderline_email_sender)
        assert features["hr_keyword_count"] > 0
        assert features["is_high_impact_context"] is True
