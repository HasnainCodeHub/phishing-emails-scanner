"""ML classifier wrapper using scikit-learn LogisticRegression.

Per contract scanner-api.md §2 and research.md R1.
"""

import os

import joblib
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.models.signal import Signal

# Human-readable display names for features
_DISPLAY_NAMES: dict[str, str] = {
    "urgency_keyword_count": "Urgent language",
    "url_count": "Links found",
    "has_suspicious_url": "Suspicious URLs",
    "sender_domain_mismatch": "Sender domain mismatch",
    "financial_keyword_count": "Financial keywords",
    "has_attachment_reference": "Attachment reference",
    "is_high_impact_context": "High-impact context",
    "executive_keyword_count": "Executive keywords",
    "hr_keyword_count": "HR keywords",
}


class ModelNotFoundError(Exception):
    """Raised when the trained model file is not found."""


class PhishingClassifier:
    """ML classifier for phishing email detection.

    Uses LogisticRegression with DictVectorizer for interpretable
    probability-based scoring and feature importance extraction.
    """

    def __init__(self, model_path: str) -> None:
        """Load trained model from disk.

        Args:
            model_path: Path to joblib-serialized model pipeline.

        Raises:
            ModelNotFoundError: If model file does not exist.
        """
        if not os.path.exists(model_path):
            raise ModelNotFoundError(f"Model not found at: {model_path}")
        self._pipeline: Pipeline = joblib.load(model_path)

    def predict(self, features: dict[str, float | int | bool]) -> tuple[int, list[Signal]]:
        """Score an email based on extracted features.

        Args:
            features: Named feature dictionary from extractor.

        Returns:
            Tuple of (risk_score 0-100, signals sorted by abs weight desc).
        """
        # Convert booleans to int for the vectorizer
        features_numeric = {
            k: int(v) if isinstance(v, bool) else v
            for k, v in features.items()
        }

        # Get probability of phishing class (class 1)
        proba = self._pipeline.predict_proba([features_numeric])[0]
        # Index 1 is the phishing probability
        phishing_prob = proba[1] if len(proba) > 1 else proba[0]
        risk_score = int(round(phishing_prob * 100))
        risk_score = max(0, min(100, risk_score))

        # Extract feature importances from the logistic regression coefficients
        vectorizer: DictVectorizer = self._pipeline.named_steps["vectorizer"]
        classifier: LogisticRegression = self._pipeline.named_steps["classifier"]

        feature_names = vectorizer.get_feature_names_out()
        coefficients = classifier.coef_[0]

        signals = []
        for fname, coef in zip(feature_names, coefficients):
            display_name = _DISPLAY_NAMES.get(fname, fname.replace("_", " ").title())
            value = features_numeric.get(fname, 0)
            signals.append(Signal(
                name=fname,
                display_name=display_name,
                value=value,
                weight=float(coef),
            ))

        # Sort by absolute weight descending
        signals.sort(key=lambda s: abs(s.weight), reverse=True)

        return risk_score, signals

    @classmethod
    def train(
        cls,
        X: list[dict],
        y: list[int],
        model_path: str,
        seed: int = 42,
    ) -> None:
        """Train and save a logistic regression model.

        Args:
            X: List of feature dictionaries.
            y: List of labels (0=safe, 1=phishing).
            model_path: Where to save the trained model.
            seed: Random seed for reproducibility.
        """
        # Convert booleans to int
        X_numeric = [
            {k: int(v) if isinstance(v, bool) else v for k, v in row.items()}
            for row in X
        ]

        pipeline = Pipeline([
            ("vectorizer", DictVectorizer(sparse=False)),
            ("classifier", LogisticRegression(
                random_state=seed,
                max_iter=1000,
                solver="lbfgs",
            )),
        ])
        pipeline.fit(X_numeric, y)

        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(pipeline, model_path)
