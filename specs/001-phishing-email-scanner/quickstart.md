# Quickstart: Explainable Phishing Email Scanner

## Prerequisites

- Python 3.13+
- UV package manager installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- OpenAI API key (for LLM escalation feature only)

## Setup

```bash
# Clone and enter the project
cd axioms-task

# Create virtual environment and install dependencies
uv sync

# Set environment variables (optional — defaults work for ML-only mode)
export OPENAI_API_KEY="sk-..."          # Required only for LLM escalation
export SCANNER_LLM_ENABLED="true"       # Default: true
export SCANNER_SAFE_THRESHOLD="45"      # Default: 45
export SCANNER_PHISHING_THRESHOLD="70"  # Default: 70
```

## Train the Model (first time only)

```bash
# Train the classifier on included training data
uv run python -m src.scoring.classifier --train
```

## Scan an Email (CLI)

```bash
# Basic scan
uv run python -m src.cli scan --email "Your urgent action required..." --sender "unknown@suspicious.com"

# Scan from file
uv run python -m src.cli scan --file path/to/email.txt --sender "sender@example.com"
```

## Expected Output

```text
=== Scan Result ===
Risk Score: 78/100
Classification: Phishing

Explanation:
This email is likely a phishing attempt. Here's why:
- This email uses urgent language 4 times, which is common in phishing attempts.
- The email contains 2 links to unfamiliar websites.
- The sender's domain does not match the organization they claim to represent.

Recommendation: Do not click any links or download attachments. Report this
email to your IT security team.

Top Signals:
- Urgent language: 4 instances (high influence)
- Suspicious URLs: 2 found (high influence)
- Sender domain mismatch: yes (medium influence)

LLM Review: Not triggered (score above phishing threshold)
```

## Run Evaluation

```bash
# Evaluate against example email set
uv run python -m src.cli evaluate
```

## Run Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/
```

## Jupyter Demo

```bash
uv run jupyter notebook notebooks/demo.ipynb
```

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| SCANNER_SAFE_THRESHOLD | 45 | Scores below → Safe |
| SCANNER_PHISHING_THRESHOLD | 70 | Scores above → Phishing |
| SCANNER_MODEL_PATH | data/model/classifier.joblib | Trained model location |
| SCANNER_LLM_ENABLED | true | Enable/disable LLM escalation |
| SCANNER_LLM_MODEL | gpt-4o-mini | LLM model for escalation |
| OPENAI_API_KEY | (none) | Required for LLM escalation |
| SCANNER_RANDOM_SEED | 42 | Training reproducibility seed |
