"""Unit tests for ML classifier module."""

import os
import tempfile

import pytest

from src.models.signal import Signal
from src.scoring.classifier import PhishingClassifier


class TestPhishingClassifier:
    """Tests for PhishingClassifier per contract scanner-api.md §2."""

    @pytest.fixture
    def trained_model_path(self):
        """Create a temporary trained model for testing."""
        training_data = [
            {"urgency_keyword_count": 0, "url_count": 0, "has_suspicious_url": 0,
             "sender_domain_mismatch": 0, "financial_keyword_count": 0,
             "has_attachment_reference": 1, "is_high_impact_context": 0,
             "executive_keyword_count": 0, "hr_keyword_count": 0},
            {"urgency_keyword_count": 5, "url_count": 3, "has_suspicious_url": 1,
             "sender_domain_mismatch": 1, "financial_keyword_count": 2,
             "has_attachment_reference": 0, "is_high_impact_context": 1,
             "executive_keyword_count": 0, "hr_keyword_count": 0},
            {"urgency_keyword_count": 0, "url_count": 1, "has_suspicious_url": 0,
             "sender_domain_mismatch": 0, "financial_keyword_count": 0,
             "has_attachment_reference": 0, "is_high_impact_context": 0,
             "executive_keyword_count": 0, "hr_keyword_count": 0},
            {"urgency_keyword_count": 3, "url_count": 2, "has_suspicious_url": 1,
             "sender_domain_mismatch": 1, "financial_keyword_count": 1,
             "has_attachment_reference": 0, "is_high_impact_context": 1,
             "executive_keyword_count": 1, "hr_keyword_count": 0},
        ]
        labels = [0, 1, 0, 1]
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, "test_model.joblib")
            PhishingClassifier.train(training_data, labels, model_path, seed=42)
            yield model_path

    def test_predict_returns_score_and_signals(self, trained_model_path, sample_features_phishing):
        classifier = PhishingClassifier(trained_model_path)
        risk_score, signals = classifier.predict(sample_features_phishing)
        assert isinstance(risk_score, int)
        assert 0 <= risk_score <= 100
        assert isinstance(signals, list)
        assert len(signals) >= 3

    def test_signals_are_signal_objects(self, trained_model_path, sample_features_phishing):
        classifier = PhishingClassifier(trained_model_path)
        _, signals = classifier.predict(sample_features_phishing)
        for signal in signals:
            assert isinstance(signal, Signal)
            assert signal.name
            assert signal.display_name
            assert isinstance(signal.weight, float)

    def test_signals_sorted_by_absolute_weight(self, trained_model_path, sample_features_phishing):
        classifier = PhishingClassifier(trained_model_path)
        _, signals = classifier.predict(sample_features_phishing)
        weights = [abs(s.weight) for s in signals]
        assert weights == sorted(weights, reverse=True)

    def test_safe_email_gets_low_score(self, trained_model_path, sample_features_safe):
        classifier = PhishingClassifier(trained_model_path)
        risk_score, _ = classifier.predict(sample_features_safe)
        assert risk_score < 50

    def test_phishing_email_gets_high_score(self, trained_model_path, sample_features_phishing):
        classifier = PhishingClassifier(trained_model_path)
        risk_score, _ = classifier.predict(sample_features_phishing)
        assert risk_score > 50

    def test_train_saves_model_to_disk(self):
        training_data = [
            {"urgency_keyword_count": 0, "url_count": 0, "has_suspicious_url": 0},
            {"urgency_keyword_count": 3, "url_count": 2, "has_suspicious_url": 1},
        ]
        labels = [0, 1]
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, "model.joblib")
            PhishingClassifier.train(training_data, labels, model_path)
            assert os.path.exists(model_path)
