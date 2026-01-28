# Research: Explainable Phishing Email Scanner

**Phase**: 0 (Outline & Research)
**Date**: 2026-01-27
**Branch**: `001-phishing-email-scanner`

## R1: ML Classifier Selection

**Decision**: Logistic Regression (scikit-learn `LogisticRegression`)

**Rationale**: Logistic regression is the simplest interpretable classifier
that provides:
- Native probability outputs via `predict_proba()` that map directly to
  the 0-100 risk score (multiply by 100).
- Coefficient-based feature importances — each feature's weight is directly
  interpretable as its influence on the phishing probability.
- Deterministic inference given fixed weights (no random components).
- Fast training and inference suitable for a local tool.

**Alternatives considered**:
- **Decision Tree (sklearn)**: Fully interpretable via tree paths but
  produces discrete probability estimates (less granular 0-100 scores).
  Prone to overfitting on small datasets.
- **Random Forest (sklearn)**: Better accuracy than single tree but feature
  importances are averaged across trees, making individual predictions
  harder to explain. Violates Constitution Principle I unless wrapped.
- **Gradient Boosted Trees (sklearn/XGBoost)**: Strong accuracy but
  feature importances are aggregate, not per-prediction. Would require
  SHAP or similar for per-prediction explanations, adding complexity.
- **Rule-based only (no ML)**: Fully deterministic but cannot generalize
  beyond hand-coded rules. Does not satisfy "ML classifier" requirement.

## R2: LLM Integration Pattern

**Decision**: OpenAI Agents SDK with single-purpose agent

**Rationale**: The OpenAI Agents SDK provides a structured agent framework
that:
- Supports defining a focused agent with a system prompt and structured
  output schema.
- Allows passing ML context (signals, score) as agent input without
  giving the agent write-access to the score.
- Logs full prompts and responses for auditability (Constitution VI).
- Handles retries and error management built-in.

**Alternatives considered**:
- **Raw OpenAI API (openai-python)**: Lower-level, requires manual
  prompt management and structured output parsing. More boilerplate.
- **LangChain**: Heavy dependency for a single-agent use case. Adds
  abstraction layers that violate Constitution complexity constraints.
- **Anthropic Claude API**: Viable alternative but user specified OpenAI
  Agents SDK explicitly.

## R3: Feature Extraction Approach

**Decision**: Pure Python regex + heuristic functions

**Rationale**: The feature extractor needs to identify text-based signals
(urgency keywords, URL patterns, sender characteristics) from raw email
text. Regex is sufficient for keyword matching and URL extraction. No NLP
library needed for the initial feature set.

**Alternatives considered**:
- **spaCy / NLTK**: NLP libraries offer entity recognition and sentiment
  analysis but add significant dependencies for features that can be
  captured with regex patterns. Deferred to future enhancement.
- **Email parsing library (email stdlib)**: Python's `email` module can
  parse MIME structure but the spec input is "raw email text" (body),
  not full MIME. May be useful if email headers are included.

## R4: Project & Dependency Management

**Decision**: UV for environment and dependency management

**Rationale**: UV is a fast Python package manager that handles:
- Virtual environment creation and management.
- Lock file generation for reproducible installs.
- Python version management.
User explicitly specified UV.

**Alternatives considered**:
- **pip + venv**: Standard but slower, no lock file by default.
- **Poetry**: Feature-rich but slower than UV, heavier configuration.
- **conda**: Overkill for a pure Python project.

## R5: Explanation Generation Strategy

**Decision**: Template-based signal-to-English mapping with LLM augmentation

**Rationale**: Each signal type maps to a plain-English template string.
This ensures:
- Consistent, jargon-free output for every scan (Constitution III).
- Deterministic explanations when LLM is not invoked.
- LLM-enhanced explanations add narrative context but never replace the
  template-based foundation.

Templates are defined as a dictionary in the explanation module, keyed by
signal name. Each template accepts the signal value as a parameter.

**Alternatives considered**:
- **LLM-only explanations**: Violates Constitution II (deterministic first)
  and would fail when LLM is unavailable.
- **Static string concatenation**: Too rigid; templates with parameters
  provide enough flexibility without complexity.

## Resolved NEEDS CLARIFICATION

All technical context fields resolved. No outstanding unknowns.
