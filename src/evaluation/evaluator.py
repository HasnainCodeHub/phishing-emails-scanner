"""Evaluator for the Phishing Email Scanner.

Computes recall (primary), precision (secondary), F1 metrics against labeled examples.
Per contract scanner-api.md §7.
"""

import json
from typing import Any

from sklearn.metrics import f1_score, precision_score, recall_score

from src.models.scan_result import EmailEvaluation, EvaluationResult, ScanResult


async def evaluate(scanner, examples: list[dict[str, Any]]) -> EvaluationResult:
    """Run scanner against labeled example emails and compute metrics.

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
    per_email_results = []

    # Process each example email
    for example in examples:
        email_text = example["email_text"]
        sender = example.get("sender", "")
        actual_label = example["label"]

        # Run the scanner on this email
        scan_result: ScanResult = await scanner.scan(email_text, sender)

        # Compare predicted vs actual
        predicted_label = scan_result.classification
        is_correct = predicted_label == actual_label

        # Create per-email evaluation result
        email_evaluation = EmailEvaluation(
            email_id=example.get("id", "unknown"),
            predicted=predicted_label,
            actual=actual_label,
            risk_score=scan_result.risk_score,
            correct=is_correct,
            signals=scan_result.signals
        )

        per_email_results.append(email_evaluation)

    # Extract true and predicted labels for metrics calculation
    y_true = [result.actual for result in per_email_results]
    y_pred = [result.predicted for result in per_email_results]

    # Convert to binary classification: Phishing vs (Safe + Suspicious)
    # This treats "Phishing" as the positive class and everything else as negative
    y_true_binary = ['Phishing' if label == 'Phishing' else 'NotPhishing' for label in y_true]
    y_pred_binary = ['Phishing' if label == 'Phishing' else 'NotPhishing' for label in y_pred]

    # Compute metrics using scikit-learn with binary classification
    recall = recall_score(y_true_binary, y_pred_binary, pos_label='Phishing', zero_division=0.0)
    precision = precision_score(y_true_binary, y_pred_binary, pos_label='Phishing', zero_division=0.0)
    f1 = f1_score(y_true_binary, y_pred_binary, pos_label='Phishing', zero_division=0.0)

    return EvaluationResult(
        recall=recall,
        precision=precision,
        f1=f1,
        per_email=per_email_results
    )


def load_examples(path: str) -> list[dict[str, Any]]:
    """Load example emails from JSON file.

    Args:
        path: Path to example emails JSON file.

    Returns:
        List of example email dictionaries.

    Raises:
        ValueError: If fewer than 3 examples are found.
    """
    with open(path, 'r', encoding='utf-8') as f:
        examples = json.load(f)

    if len(examples) < 3:
        raise ValueError(f"Expected at least 3 example emails, found {len(examples)}")

    return examples