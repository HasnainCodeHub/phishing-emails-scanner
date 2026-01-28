"""Unit tests for rule-based classification module."""

import pytest

from src.decision.rules import classify


class TestClassify:
    """Tests for classify() per contract scanner-api.md §3."""

    def test_safe_score(self):
        classification, is_borderline, is_high_impact = classify(
            30, {"is_high_impact_context": False}
        )
        assert classification == "Safe"
        assert is_borderline is False
        assert is_high_impact is False

    def test_suspicious_score(self):
        classification, is_borderline, is_high_impact = classify(
            55, {"is_high_impact_context": False}
        )
        assert classification == "Suspicious"
        assert is_borderline is True

    def test_phishing_score(self):
        classification, is_borderline, is_high_impact = classify(
            85, {"is_high_impact_context": False}
        )
        assert classification == "Phishing"
        assert is_borderline is False
        assert is_high_impact is False

    def test_boundary_score_45_is_suspicious(self):
        classification, is_borderline, _ = classify(
            45, {"is_high_impact_context": False}
        )
        assert classification == "Suspicious"
        assert is_borderline is True

    def test_boundary_score_70_is_suspicious(self):
        classification, is_borderline, _ = classify(
            70, {"is_high_impact_context": False}
        )
        assert classification == "Suspicious"
        assert is_borderline is True

    def test_score_44_is_safe(self):
        classification, _, _ = classify(44, {"is_high_impact_context": False})
        assert classification == "Safe"

    def test_score_71_is_phishing(self):
        classification, _, _ = classify(71, {"is_high_impact_context": False})
        assert classification == "Phishing"

    def test_high_impact_context(self):
        _, _, is_high_impact = classify(30, {"is_high_impact_context": True})
        assert is_high_impact is True

    def test_configurable_thresholds(self):
        classification, _, _ = classify(
            50, {"is_high_impact_context": False},
            safe_threshold=60, phishing_threshold=80,
        )
        assert classification == "Safe"

    def test_configurable_thresholds_phishing(self):
        classification, _, _ = classify(
            90, {"is_high_impact_context": False},
            safe_threshold=60, phishing_threshold=80,
        )
        assert classification == "Phishing"
