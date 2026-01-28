# Implementation Plan: Explainable Phishing Email Scanner

**Branch**: `001-phishing-email-scanner` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phishing-email-scanner/spec.md`

## Summary

Build an explainable phishing email scanner that accepts raw email text and
a sender identifier, produces a risk score (0-100), classification (Safe /
Suspicious / Phishing), and a plain-English explanation. The primary
classification uses a scikit-learn interpretable ML classifier with
feature-level signal exposure. Conditional LLM escalation via OpenAI Agents
SDK handles borderline scores (45-70) and high-impact contexts. Evaluation
uses recall-prioritized metrics against a curated example set.

## Technical Context

**Language/Version**: Python 3.13+
**Package Manager**: UV for dependency and environment management
**Primary Dependencies**: scikit-learn (ML classifier + metrics), openai-agents (LLM escalation), regex (stdlib)
**Storage**: File-based (model artifacts as joblib/pickle, example emails as JSON fixtures)
**Testing**: pytest (unit + integration)
**Target Platform**: Local development / CLI / Jupyter Notebook
**Project Type**: Single project
**Performance Goals**: Single-email scan < 2s without LLM, < 10s with LLM escalation
**Constraints**: No end-to-end LLM classification; LLM invoked only via explicit escalation rules; deterministic ML inference
**Scale/Scope**: Single-user local tool; evaluation against 3+ example emails

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Gate | Status |
|---|-----------|------|--------|
| I | Explainability Over Accuracy | ML model must expose feature importances; scikit-learn classifiers natively support this | PASS |
| II | Deterministic ML First, LLM Second | ML classifier is primary; LLM via OpenAI Agents SDK is conditional on score range (45-70) or high-impact context | PASS |
| III | Clear Non-Technical Explanations | Explanation generator module translates signals to plain English; no jargon in output | PASS |
| IV | Modular Spec-Driven Architecture | Four distinct layers (extraction, scoring, decision, escalation) with clear contracts | PASS |
| V | Recall-Sensitive Validation | scikit-learn metrics provide recall/precision; evaluation module prioritizes recall | PASS |
| VI | Reproducibility and Testability | Fixed random seeds for training; deterministic inference; pytest test suite; externalized config | PASS |

All gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-phishing-email-scanner/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── scanner-api.md   # Internal module contracts
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── config.py                 # Externalized thresholds, model paths, feature flags
├── models/
│   ├── __init__.py
│   ├── email_submission.py   # Email input data structure
│   ├── scan_result.py        # Scan output data structure
│   └── signal.py             # Signal data structure
├── features/
│   ├── __init__.py
│   └── extractor.py          # Feature extraction (regex + heuristics)
├── scoring/
│   ├── __init__.py
│   └── classifier.py         # ML classifier wrapper (scikit-learn)
├── decision/
│   ├── __init__.py
│   └── rules.py              # Threshold-based classification rules
├── escalation/
│   ├── __init__.py
│   └── llm_agent.py          # OpenAI Agents SDK escalation
├── explanation/
│   ├── __init__.py
│   └── generator.py          # Plain-English explanation builder
├── evaluation/
│   ├── __init__.py
│   └── evaluator.py          # Metric computation (recall, precision, F1)
├── pipeline/
│   ├── __init__.py
│   └── scanner.py            # Orchestrator: extraction → scoring → decision → escalation → explanation
└── cli.py                    # CLI entry point

tests/
├── __init__.py
├── conftest.py               # Shared fixtures (example emails, mock model)
├── unit/
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_classifier.py
│   ├── test_rules.py
│   ├── test_llm_agent.py
│   ├── test_generator.py
│   └── test_evaluator.py
├── integration/
│   ├── __init__.py
│   ├── test_pipeline.py      # End-to-end scan without LLM
│   └── test_pipeline_llm.py  # End-to-end scan with LLM (mocked)
└── fixtures/
    └── example_emails.json   # Curated labeled example emails

data/
├── model/                    # Trained model artifacts (gitignored)
│   └── .gitkeep
└── training/                 # Training data (gitignored)
    └── .gitkeep

notebooks/
└── demo.ipynb                # Jupyter demo notebook
```

**Structure Decision**: Single project layout. The system is a local Python
tool with no frontend/backend split. All source code lives under `src/` with
clear module boundaries matching the four processing layers (features,
scoring, decision, escalation) plus explanation, evaluation, and pipeline
orchestration.

## Architecture

### Processing Pipeline

```text
Email Text + Sender
       │
       ▼
┌──────────────────┐
│ Feature Extractor │  → Extract signals (regex, heuristics)
│  src/features/    │     Output: dict of named features
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  ML Classifier    │  → Score email (0-100) + feature importances
│  src/scoring/     │     Output: risk_score, signal list
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Rule Engine      │  → Apply thresholds: Safe (<45), Suspicious (45-70), Phishing (>70)
│  src/decision/    │     Output: classification label
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│  Escalation Check     │  → Borderline (45-70) OR high-impact context?
│  src/escalation/      │     YES → invoke LLM agent for review
│                       │     NO  → skip LLM
└──────┬───────────────┘
       │
       ▼
┌──────────────────┐
│  Explanation Gen  │  → Build plain-English explanation from signals
│  src/explanation/ │     + optional LLM-enhanced reasoning
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Scan Result      │  → risk_score + classification + explanation
│  src/models/      │     + signals + llm_escalated flag
└──────────────────┘
```

### Key Design Decisions

1. **Classifier Choice: Logistic Regression** — Logistic regression with
   L2 regularization provides native probability outputs (calibrated
   `predict_proba`) that map directly to the 0-100 risk score, and
   coefficient-based feature importances for explainability. This is the
   simplest classifier that satisfies all constitution principles.

2. **Feature Extraction: Regex + Heuristics** — Pure Python with stdlib
   `re` module. Features include: urgency keyword count, URL count,
   URL domain age signals, sender domain match, attachment indicators,
   financial keyword density, executive/HR context markers. Each feature
   has a human-readable name.

3. **LLM Integration: OpenAI Agents SDK** — A single agent with a focused
   system prompt receives the ML signals and score, then produces a
   structured review. The agent never receives the ability to modify the
   risk score — it only outputs an explanation and optional verdict
   label suggestion. LLM calls are fully logged (prompt + response).

4. **Explanation Templates** — Signal-to-English mapping via a template
   system. Each known signal type has a plain-English template (e.g.,
   "urgency_keyword_count" → "This email uses urgent language {n} times,
   which is common in phishing attempts"). LLM-enhanced explanations
   augment but do not replace template-based explanations.

5. **Configuration Externalization** — All thresholds (45, 70), model
   paths, LLM parameters, and feature flags stored in `src/config.py`
   with environment variable overrides. No magic numbers in code.

### High-Impact Context Detection

Keywords-based heuristic in the feature extractor:
- **Finance**: "invoice", "payment", "wire transfer", "bank account",
  "tax", "billing"
- **HR**: "benefits", "payroll", "salary", "termination", "offer letter"
- **Executive**: Sender domain matching known executive names/patterns,
  "CEO", "CFO", "board", "confidential"

The context detection produces a boolean flag consumed by the escalation
module. The keyword lists are externalized in config for easy updates.

## Complexity Tracking

> No constitution violations detected. No complexity justifications needed.

## Module Contracts

See [contracts/scanner-api.md](./contracts/scanner-api.md) for full
interface definitions.

### Summary of Module Interfaces

| Module | Input | Output |
|--------|-------|--------|
| Feature Extractor | raw_email_text: str, sender: str | dict[str, float\|int\|bool] (named features) |
| ML Classifier | features: dict[str, float\|int\|bool] | risk_score: int (0-100), signals: list[Signal] |
| Rule Engine | risk_score: int, features: dict | classification: str, is_borderline: bool, is_high_impact: bool |
| LLM Escalation | scan context (score, signals, classification, email excerpt) | llm_explanation: str, suggested_label: str\|None, rationale: str |
| Explanation Generator | signals: list[Signal], classification: str, llm_output: Optional | explanation: str (plain English) |
| Pipeline (Scanner) | email_text: str, sender: str | ScanResult (score, classification, explanation, signals, llm_escalated) |
| Evaluator | predictions: list[ScanResult], labels: list[str] | recall: float, precision: float, f1: float, per_email: list |
