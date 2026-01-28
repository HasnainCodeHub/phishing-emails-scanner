<!--
=== Sync Impact Report ===
Version change: 0.0.0 → 1.0.0 (initial ratification)
Modified principles: N/A (first version)
Added sections:
  - Principle I: Explainability Over Accuracy
  - Principle II: Deterministic ML First, LLM Second
  - Principle III: Clear Non-Technical Explanations
  - Principle IV: Modular Spec-Driven Architecture
  - Principle V: Recall-Sensitive Validation
  - Principle VI: Reproducibility and Testability
  - Section: Functional Rules
  - Section: Non-Functional Constraints
  - Governance
Removed sections: N/A (first version)
Templates requiring updates:
  - .specify/templates/plan-template.md — ⚠ pending
    (Constitution Check section needs gates derived from
    these principles at plan time)
  - .specify/templates/spec-template.md — ✅ no changes needed
    (template is generic; principles apply at fill time)
  - .specify/templates/tasks-template.md — ✅ no changes needed
    (template is generic; principles apply at fill time)
Follow-up TODOs: none
-->

# Axioms Phishing Scanner Constitution

## Core Principles

### I. Explainability Over Accuracy

Every design and implementation decision MUST favor explainability
when it conflicts with marginal accuracy gains. Users MUST be able
to understand why an email was flagged, not just that it was flagged.

- The ML model MUST expose its top contributing signals
  (e.g., feature importances, rule triggers) for every prediction.
- No opaque ensemble or black-box model is permitted unless its
  outputs are wrapped in a transparent explanation layer.
- Accuracy improvements that degrade explainability MUST be
  rejected unless a compensating explanation mechanism is provided
  and documented.

**Rationale**: User trust is the primary product metric. A scanner
that users do not trust will not be used, regardless of accuracy.

### II. Deterministic ML First, LLM Second

The primary classification pipeline MUST use deterministic,
interpretable ML models. LLM usage is strictly conditional and
secondary.

- The ML model produces the initial risk score (0-100) and
  classification (Safe / Suspicious / Phishing) for every email.
- LLM invocation is permitted ONLY when:
  - The risk score falls in the borderline range (approximately
    45-70), OR
  - The email context is high-impact (finance, HR, executive
    communications).
- The LLM MUST NOT blindly override the ML model's output. Any
  LLM-driven adjustment MUST be logged with rationale and bounded
  by configurable limits.
- When the LLM is not invoked, the system MUST still produce a
  complete, valid output (score + classification + explanation).

**Rationale**: Deterministic models are reproducible, auditable,
and fast. LLMs add value in ambiguous cases but introduce latency,
cost, and non-determinism that MUST be controlled.

### III. Clear Non-Technical Explanations

Every email analysis MUST produce a plain-English explanation that
a non-technical user can understand without security expertise.

- Explanations MUST avoid jargon (e.g., "DKIM failure" should
  become "the sender's identity could not be verified").
- Explanations MUST reference the specific signals that drove the
  classification (e.g., "this email contains a link to an
  unfamiliar domain that was registered recently").
- Explanation quality is a first-class acceptance criterion for
  every feature that touches the output pipeline.

**Rationale**: The scanner serves end users who need actionable
guidance, not raw technical telemetry.

### IV. Modular Spec-Driven Architecture

The system MUST be composed of well-defined, independently testable
modules following spec-driven development practices.

- Each module (feature extraction, scoring, explanation generation,
  LLM integration) MUST have a clear interface contract.
- Modules MUST be replaceable without cascading changes (e.g.,
  swapping the ML model MUST NOT require changes to the explanation
  generator beyond adapter updates).
- All features MUST go through the spec-plan-tasks workflow before
  implementation begins.
- No module may introduce hidden coupling to another module's
  internals.

**Rationale**: Modularity enables independent testing, parallel
development, and safe iteration on individual components.

### V. Recall-Sensitive Validation

Evaluation and validation MUST prioritize recall (minimizing false
negatives) over precision, because a missed phishing email is more
harmful than a false alarm.

- The primary evaluation metric MUST be recall at a defined
  threshold, with precision tracked as a secondary metric.
- Example-driven validation MUST be included: a curated set of
  known phishing and legitimate emails MUST be maintained and used
  in automated tests.
- Failure modes (false negatives and false positives) MUST be
  documented with root-cause analysis and improvement plans.

**Rationale**: In a security context, failing to detect a phishing
email exposes users to real harm. False positives are annoying but
recoverable.

### VI. Reproducibility and Testability

Every pipeline run MUST be reproducible given the same inputs, and
every component MUST be independently testable.

- ML model predictions MUST be deterministic given fixed model
  weights and input features (no random seeds at inference time).
- LLM calls MUST log full prompts and responses for auditability.
- Test suites MUST cover: unit tests per module, integration tests
  for the full pipeline, and regression tests against the example
  validation set.
- All configuration (thresholds, feature flags, model paths) MUST
  be externalized, never hardcoded.

**Rationale**: A security tool that produces inconsistent results
undermines user trust and complicates debugging.

## Functional Rules

Every email processed by the scanner MUST produce all three outputs:

1. **Risk Score** (integer 0-100): quantifies phishing likelihood.
2. **Classification**: one of `Safe`, `Suspicious`, or `Phishing`.
3. **Plain-English Explanation**: human-readable summary of the
   signals that drove the classification.

Additional functional constraints:

- The ML model MUST expose its top contributing signals alongside
  the score.
- LLM usage boundaries:
  - Borderline risk scores: approximately 45-70.
  - High-impact contexts: finance, HR, executive communications.
- The LLM MUST NOT override the ML classification without bounded,
  logged justification.

## Non-Functional Constraints

- **Model Selection**: Use lightweight, interpretable ML models
  (e.g., logistic regression, decision trees, gradient-boosted
  trees with feature importance). Deep neural networks are
  permitted only if wrapped in an explanation layer.
- **Complexity**: Avoid unnecessary abstraction. Every layer of
  indirection MUST justify its existence with a clear benefit.
- **Reproducibility**: Fixed seeds for training; deterministic
  inference; versioned model artifacts.
- **Testability**: Every module MUST be testable in isolation with
  synthetic inputs. No module may require a live external service
  for unit tests.

## Governance

This constitution is the authoritative source for project
principles and constraints. All implementation decisions, code
reviews, and architectural choices MUST be evaluated against
these principles.

- **Amendment Process**: Any change to this constitution MUST be
  proposed as a pull request with rationale, reviewed by the
  project lead, and documented with a version bump.
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH).
  - MAJOR: Principle removal or incompatible redefinition.
  - MINOR: New principle or material expansion of guidance.
  - PATCH: Clarifications, wording, non-semantic refinements.
- **Compliance Review**: Every PR and design review MUST include
  a constitution compliance check. Non-compliance MUST be
  justified and documented as a complexity violation.
- **Conflict Resolution**: When principles conflict (e.g.,
  explainability vs. recall), the higher-numbered principle
  yields to the lower-numbered one unless explicitly justified
  in an ADR.

**Version**: 1.0.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-01-27
