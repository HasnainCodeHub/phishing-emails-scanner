"""Pipeline orchestrator: extraction -> scoring -> decision -> escalation -> explanation.

Per contract scanner-api.md §6.
"""

from src.config import ScannerConfig
from src.decision.rules import classify
from src.explanation.generator import generate_explanation
from src.features.extractor import extract_features
from src.models.scan_result import ScanResult
from src.scoring.classifier import PhishingClassifier


class EmailScanner:
    """Orchestrates the full email scanning pipeline.

    Pipeline steps:
    1. Validate input
    2. Extract features
    3. Score with ML classifier
    4. Apply rule-based classification
    5. Check escalation triggers
    6. If triggered and LLM enabled: escalate to LLM
    7. Generate explanation
    8. Return ScanResult
    """

    def __init__(self, config: ScannerConfig | None = None) -> None:
        """Initialize scanner with configuration and load model."""
        self.config = config or ScannerConfig()
        self._classifier = PhishingClassifier(self.config.model_path)

    async def scan(self, email_text: str, sender: str) -> ScanResult:
        """Scan a single email through the full pipeline.

        Args:
            email_text: Raw email body text.
            sender: Sender identifier string.

        Returns:
            ScanResult with all required fields populated.

        Raises:
            ValueError: If email_text is empty or whitespace-only.
        """
        # Step 1: Validate input (extract_features raises ValueError)
        # Step 2: Extract features
        features = extract_features(email_text, sender, self.config)

        # Step 3: Score with ML classifier
        risk_score, signals = self._classifier.predict(features)

        # Step 4: Apply rule-based classification
        classification, is_borderline, is_high_impact = classify(
            risk_score,
            features,
            safe_threshold=self.config.safe_threshold,
            phishing_threshold=self.config.phishing_threshold,
        )

        # Step 5: Check escalation triggers
        should_escalate = (is_borderline or is_high_impact) and self.config.llm_enabled
        llm_output = None
        llm_escalated = False

        if should_escalate:
            llm_escalated, llm_output = await self._try_escalate(
                email_text, sender, risk_score, classification, signals
            )

        # Step 7: Generate explanation
        explanation = generate_explanation(classification, signals, risk_score, llm_output)

        # Step 8: Return ScanResult
        return ScanResult(
            risk_score=risk_score,
            classification=classification,
            explanation=explanation,
            signals=signals,
            llm_escalated=llm_escalated,
            llm_output=llm_output,
        )

    async def _try_escalate(self, email_text, sender, risk_score, classification, signals):
        """Attempt LLM escalation with fallback.

        Returns:
            Tuple of (llm_escalated: bool, llm_output: LLMReviewResult | None)
        """
        from src.escalation.llm_agent import escalate, LLMUnavailableError
        try:
            llm_output = await escalate(
                email_text, sender, risk_score, classification, signals
            )
            return True, llm_output
        except LLMUnavailableError:
            # FR-013: Fall back to ML-only result
            return False, None
