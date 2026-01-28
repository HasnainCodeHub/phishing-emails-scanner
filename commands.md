# CLI Commands

## Run the Project

```bash
uv run python main.py
```

Runs the scanner against three built-in test emails (safe, phishing, borderline) and displays full results with LLM escalation.

## Scan an Email

Scan inline text:

```bash
uv run python -m src.cli scan --email "Your account has been compromised! Click here now!" --sender "alert@bank.com"
```

Scan from a file:

```bash
uv run python -m src.cli scan --file path/to/email.txt --sender "sender@example.com"
```

## Train the Model

Train using the Kaggle phishing email dataset (auto-downloads if not present):

```bash
uv run python -m src.cli train
```

Train with a custom dataset:

```bash
uv run python -m src.cli train --data data/training/phishing_email.csv
```

## Evaluate the Model

Run evaluation against example emails:

```bash
uv run python -m src.cli evaluate
```

Evaluate with custom examples:

```bash
uv run python -m src.cli evaluate --examples path/to/examples.json
```

## Run Tests

Run all tests:

```bash
uv run pytest tests/ -v
```

Run only unit tests:

```bash
uv run pytest tests/unit/ -v
```

Run only integration tests:

```bash
uv run pytest tests/integration/ -v
```

## Environment Setup

1. Copy `.env.example` to `.env` and add your Gemini API key:

```bash
cp .env.example .env
```

2. Set `GEMINI_API_KEY` in `.env`:

```
GEMINI_API_KEY=your_api_key_here
```

3. Install dependencies:

```bash
uv sync
```
