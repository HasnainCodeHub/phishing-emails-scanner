# Explainable Phishing Email Scanner

An ML-first phishing email scanner with conditional LLM escalation, built for transparency and user trust.

## Architecture

The scanner follows a modular pipeline architecture:

```
Input Email → Feature Extraction → ML Classification → Rule Engine → LLM Escalation? → Explanation Generation → Output
```

**Pipeline Steps:**
1. **Feature Extraction**: Extracts named features (urgency keywords, URLs, sender mismatches, etc.)
2. **ML Classification**: Uses LogisticRegression to produce risk score (0-100) and top contributing signals
3. **Rule Engine**: Applies threshold-based classification:
   - Safe: <45
   - Suspicious: 45-70
   - Phishing: >70
4. **LLM Escalation**: Conditionally triggers for borderline scores (45-70) or high-impact contexts (finance/HR/executive)
5. **Explanation Generation**: Creates plain-English explanations referencing ML signals and optionally LLM insights

## Design Decisions

### 1. ML Classifier Choice (Research.md R1)
- **LogisticRegression** selected over Decision Trees/Random Forest for:
  - Direct coefficient interpretation for explainability
  - Feature importance ranking for signal identification
  - Fast, deterministic inference
  - Linear combination transparency

### 2. LLM Integration (Research.md R2)
- **OpenAI Agents SDK** for structured agent definition
- Conditional escalation only for borderline cases or high-impact contexts
- LLM never modifies ML risk score (preserves determinism)

### 3. Explanation Strategy (Research.md R5)
- Template-based explanations referencing specific ML signals
- LLM augmentation for nuanced reasoning (when available)
- Plain-English output avoiding technical jargon

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd axioms-task

# Install dependencies with UV
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env to add OPENAI_API_KEY if using LLM escalation
```

## Usage

### CLI Commands

```bash
# Scan an email
uv run python -m src.cli scan --sender "sender@example.com" --email "Email content here..."

# Scan from file
uv run python -m src.cli scan --sender "sender@example.com" --file "path/to/email.txt"

# Train the model
uv run python -m src.cli train --data "path/to/training-data.json"

# Evaluate against example emails
uv run python -m src.cli evaluate
```

### Python API

```python
from src.config import ScannerConfig
from src.pipeline.scanner import EmailScanner

# Initialize scanner
config = ScannerConfig()
scanner = EmailScanner(config)

# Scan an email
result = await scanner.scan("Email content", "sender@example.com")

print(f"Risk Score: {result.risk_score}")
print(f"Classification: {result.classification}")
print(f"Explanation: {result.explanation}")
```

## Example Output

```
=== Scan Result ===
Risk Score: 82/100
Classification: Phishing

Explanation:
This email is likely a phishing attempt.

Here's why:
- This email uses urgent language 3 times, which is common in phishing attempts.
- The email contains links to unfamiliar or suspicious websites.
- The sender's domain does not match the websites referenced in the email.

Enhanced Review:
The LLM review confirms this is likely phishing based on the urgent language, suspicious links, and sender spoofing.

Recommendation:
Do not click any links or download attachments from this email. Report it to your IT security team and delete it.
```

## Failure Modes & Error Handling

- **Empty Input**: Raises `ValueError` for empty email text
- **LLM Unavailable**: Gracefully falls back to ML-only explanation with note
- **Threshold Boundaries**: Score <45 → Safe, 45-70 → Suspicious, >70 → Phishing
- **Configuration**: All thresholds and paths externalized via environment variables

## Future Improvements

- **NLP Features**: Advanced text embeddings and semantic analysis
- **Model Ensemble**: Multiple models with unified explanation wrapper
- **Real-time Integration**: Direct email server integration
- **Extended Context Detection**: Additional high-impact scenarios beyond finance/HR/executive
- **Multilingual Support**: Non-English phishing detection

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## License

MIT