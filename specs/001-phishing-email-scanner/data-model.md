# Data Model: Explainable Phishing Email Scanner

**Phase**: 1 (Design & Contracts)
**Date**: 2026-01-27
**Branch**: `001-phishing-email-scanner`

## Entities

### EmailSubmission

The input to the scanner pipeline.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| email_text | str | Raw email body text | MUST NOT be empty or whitespace-only |
| sender | str | Sender identifier (email address or name) | May be empty; system notes missing sender in explanation |

### Signal

A single feature-level influence on the classification.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| name | str | Human-readable signal name (e.g., "urgency_keyword_count") | MUST be non-empty |
| display_name | str | Plain-English label (e.g., "Urgent language") | MUST avoid technical jargon |
| value | float or int or bool | Extracted feature value | Required |
| weight | float | Contribution weight toward risk score (from classifier coefficients) | Required |

### ScanResult

The complete output of scanning a single email.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| risk_score | int | Phishing confidence score (0-100) | MUST be in range [0, 100] |
| classification | str | One of: "Safe", "Suspicious", "Phishing" | MUST be one of exactly these three values |
| explanation | str | Plain-English explanation answering verdict, reasoning, next steps | MUST NOT be empty |
| signals | list[Signal] | Top contributing signals from ML classifier | MUST contain >= 3 signals |
| llm_escalated | bool | Whether LLM review was triggered | Required |
| llm_output | LLMReviewResult or None | LLM review output if escalated | None when not escalated |

### LLMReviewResult

Output from the LLM escalation agent.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| llm_explanation | str | LLM-generated reasoning summary | MUST NOT be empty |
| suggested_label | str or None | Optional refined verdict label | If present, must be "Safe", "Suspicious", or "Phishing" |
| rationale | str | Justification referencing ML signals | MUST reference at least one ML signal by name |
| prompt_log | str | Full prompt sent to LLM | Required for auditability |
| response_log | str | Full LLM response | Required for auditability |

### EvaluationResult

Aggregate output from running evaluation against labeled examples.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| recall | float | Recall score (primary metric) | In range [0.0, 1.0] |
| precision | float | Precision score (secondary metric) | In range [0.0, 1.0] |
| f1 | float | F1 score | In range [0.0, 1.0] |
| per_email | list[EmailEvaluation] | Per-email prediction vs. actual | MUST have >= 3 entries |

### EmailEvaluation

Per-email evaluation detail.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| email_id | str | Identifier for the example email | Required |
| predicted | str | Predicted classification | Required |
| actual | str | Ground-truth label | Required |
| risk_score | int | Predicted risk score | Required |
| correct | bool | Whether predicted matches actual | Required |
| signals | list[Signal] | Signals that drove the prediction | Required |

### ExampleEmail

A labeled email in the curated validation set.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | str | Unique identifier | Required |
| email_text | str | Raw email body text | Required |
| sender | str | Sender identifier | Required |
| label | str | Ground-truth classification: "Safe", "Suspicious", or "Phishing" | Required |
| description | str | Brief description of why this email has this label | Optional |

## Relationships

```text
EmailSubmission ──[scanned by]──→ Pipeline ──→ ScanResult
                                                  │
                                                  ├── signals: list[Signal]
                                                  └── llm_output: LLMReviewResult (optional)

ExampleEmail ──[evaluated by]──→ Evaluator ──→ EvaluationResult
                                                  └── per_email: list[EmailEvaluation]
```

## State Transitions

The scan pipeline is stateless — each email is processed independently.
No persistent state transitions exist. Model artifacts are loaded once
at initialization and remain immutable during inference.

## Configuration

| Parameter | Default | Env Override | Description |
|-----------|---------|--------------|-------------|
| SAFE_THRESHOLD | 45 | SCANNER_SAFE_THRESHOLD | Scores below this are Safe |
| PHISHING_THRESHOLD | 70 | SCANNER_PHISHING_THRESHOLD | Scores above this are Phishing |
| MODEL_PATH | data/model/classifier.joblib | SCANNER_MODEL_PATH | Path to trained model artifact |
| LLM_ENABLED | true | SCANNER_LLM_ENABLED | Feature flag for LLM escalation |
| LLM_MODEL | gpt-4o-mini | SCANNER_LLM_MODEL | LLM model identifier |
| RANDOM_SEED | 42 | SCANNER_RANDOM_SEED | Fixed seed for training reproducibility |
