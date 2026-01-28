# Module Contracts: Explainable Phishing Email Scanner

**Phase**: 1 (Design & Contracts)
**Date**: 2026-01-27

This document defines the internal module interfaces. The system has no
external HTTP API — all contracts are Python function/class interfaces.

## 1. Feature Extractor

**Module**: `src/features/extractor.py`

```python
def extract_features(email_text: str, sender: str) -> dict[str, float | int | bool]:
    """
    Extract named features from raw email text and sender.

    Args:
        email_text: Raw email body text (validated non-empty).
        sender: Sender identifier string (may be empty).

    Returns:
        Dictionary mapping feature names to their values.
        Feature names are human-readable identifiers.

    Example output:
        {
            "urgency_keyword_count": 3,
            "url_count": 2,
            "has_suspicious_url": True,
            "sender_domain_mismatch": True,
            "financial_keyword_count": 1,
            "has_attachment_reference": False,
            "is_high_impact_context": True,
            "executive_keyword_count": 0,
            "hr_keyword_count": 0,
        }

    Raises:
        ValueError: If email_text is empty or whitespace-only.
    """
```

## 2. ML Classifier

**Module**: `src/scoring/classifier.py`

```python
class PhishingClassifier:
    def __init__(self, model_path: str):
        """Load trained model from disk."""

    def predict(self, features: dict[str, float | int | bool]) -> tuple[int, list[Signal]]:
        """
        Score an email based on extracted features.

        Args:
            features: Named feature dictionary from extractor.

        Returns:
            Tuple of:
            - risk_score: int (0-100), probability-like confidence of phishing
            - signals: list[Signal], top contributing features sorted by
              absolute weight descending. Minimum 3 signals.

        The risk_score is derived from the model's predict_proba output
        multiplied by 100 and rounded to nearest integer.
        """

    @classmethod
    def train(cls, X: list[dict], y: list[int], model_path: str, seed: int = 42):
        """
        Train and save a logistic regression model.

        Args:
            X: List of feature dictionaries.
            y: List of labels (0=safe, 1=phishing).
            model_path: Where to save the trained model.
            seed: Random seed for reproducibility.
        """
```

## 3. Rule Engine

**Module**: `src/decision/rules.py`

```python
def classify(
    risk_score: int,
    features: dict[str, float | int | bool],
    safe_threshold: int = 45,
    phishing_threshold: int = 70,
) -> tuple[str, bool, bool]:
    """
    Apply rule-based thresholds to determine classification.

    Args:
        risk_score: ML-produced score (0-100).
        features: Named feature dictionary (used for high-impact detection).
        safe_threshold: Scores below this are "Safe" (default 45).
        phishing_threshold: Scores above this are "Phishing" (default 70).

    Returns:
        Tuple of:
        - classification: "Safe" | "Suspicious" | "Phishing"
        - is_borderline: True if score in [safe_threshold, phishing_threshold]
        - is_high_impact: True if finance/HR/executive context detected

    Boundary rules:
        - score < safe_threshold → "Safe"
        - score > phishing_threshold → "Phishing"
        - safe_threshold <= score <= phishing_threshold → "Suspicious"
    """
```

## 4. LLM Escalation

**Module**: `src/escalation/llm_agent.py`

```python
async def escalate(
    email_text: str,
    sender: str,
    risk_score: int,
    classification: str,
    signals: list[Signal],
) -> LLMReviewResult:
    """
    Invoke LLM agent for secondary review of borderline/high-impact email.

    Args:
        email_text: Raw email text (truncated to first 2000 chars for LLM).
        sender: Sender identifier.
        risk_score: ML-produced score (read-only, not modifiable).
        classification: ML-determined classification.
        signals: Top contributing signals from ML model.

    Returns:
        LLMReviewResult with explanation, optional label suggestion,
        rationale referencing ML signals, and full prompt/response logs.

    Raises:
        LLMUnavailableError: If LLM service cannot be reached.
            Caller must handle fallback to ML-only explanation.
    """
```

## 5. Explanation Generator

**Module**: `src/explanation/generator.py`

```python
def generate_explanation(
    classification: str,
    signals: list[Signal],
    llm_output: LLMReviewResult | None = None,
) -> str:
    """
    Build a plain-English explanation from signals and optional LLM output.

    The explanation MUST answer:
    1. What is the verdict?
    2. Why was this decision made?
    3. What should the user do next?

    Args:
        classification: "Safe", "Suspicious", or "Phishing".
        signals: Top contributing signals with human-readable names.
        llm_output: Optional LLM review result for enhanced reasoning.

    Returns:
        Plain-English string. No technical jargon. References specific
        signals by their display names.
    """
```

## 6. Pipeline (Scanner)

**Module**: `src/pipeline/scanner.py`

```python
class EmailScanner:
    def __init__(self, config: ScannerConfig):
        """Initialize scanner with configuration and load model."""

    async def scan(self, email_text: str, sender: str) -> ScanResult:
        """
        Scan a single email through the full pipeline.

        Pipeline steps:
        1. Validate input (reject empty email_text)
        2. Extract features
        3. Score with ML classifier
        4. Apply rule-based classification
        5. Check escalation triggers (borderline OR high-impact)
        6. If triggered and LLM enabled: escalate to LLM
        7. Generate explanation (with or without LLM output)
        8. Return ScanResult

        Args:
            email_text: Raw email body text.
            sender: Sender identifier string.

        Returns:
            ScanResult with all required fields populated.

        Raises:
            ValueError: If email_text is empty or whitespace-only.
        """
```

## 7. Evaluator

**Module**: `src/evaluation/evaluator.py`

```python
async def evaluate(
    scanner: EmailScanner,
    examples: list[ExampleEmail],
) -> EvaluationResult:
    """
    Run scanner against labeled example emails and compute metrics.

    Args:
        scanner: Configured EmailScanner instance.
        examples: List of labeled example emails (minimum 3).

    Returns:
        EvaluationResult with recall (primary), precision (secondary),
        F1, and per-email breakdown including signals and correctness.

    Metrics are computed using scikit-learn:
    - recall_score(y_true, y_pred, average='binary', pos_label='Phishing')
    - precision_score(y_true, y_pred, average='binary', pos_label='Phishing')
    - f1_score(y_true, y_pred, average='binary', pos_label='Phishing')
    """
```

## Error Taxonomy

| Error | Module | HTTP-equiv | Description |
|-------|--------|------------|-------------|
| ValueError | Feature Extractor, Pipeline | 400 | Empty or whitespace-only email text |
| LLMUnavailableError | LLM Escalation | 503 | LLM service unreachable; pipeline falls back to ML-only |
| ModelNotFoundError | ML Classifier | 500 | Trained model file not found at configured path |
