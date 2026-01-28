# Feature Specification: Explainable Phishing Email Scanner

**Feature Branch**: `001-phishing-email-scanner`
**Created**: 2026-01-27
**Status**: Draft
**Input**: User description: "Explainable phishing email scanning system with ML-first classification, conditional LLM escalation, and plain-English explanations"

## Clarifications

### Session 2026-01-27

- Q: What does the risk score semantically represent? → A: Probability-like confidence of phishing (0-100). Thresholds are guideline-based, adjustable, and must remain explainable.
- Q: What classification label applies to borderline scores? → A: Borderline range (45-70) MUST produce "Suspicious" classification unless overridden by explicit rules. "Borderline" describes the score range; "Suspicious" is the output label.
- Q: What authority does the LLM have over the ML output? → A: LLM provides secondary review and explanation only. LLM MUST NOT change the ML risk score value. LLM may suggest a refined verdict label but must reference ML signals.
- Q: What does "top contributing signals" mean? → A: Feature-level influences on the classification (e.g., "sender domain age", "urgency keyword count"), not raw model internals (weights, coefficients). Explanations must avoid technical ML terminology.
- Q: How is the dataset used? → A: Dataset is used for model training and evaluation only. Example emails used for demonstration may be synthetic or selected samples.
- Q: What happens when the LLM is unavailable? → A: System must fall back to ML-based explanation only. No degradation of core output structure.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Scan an Email and Get a Verdict (Priority: P1)

A user submits a raw email text and sender identifier. The system
analyzes the email using an interpretable ML classifier, produces a
risk score (0-100), classifies it as Safe, Suspicious, or Phishing,
and returns a plain-English explanation describing the verdict, the
reasoning, and what the user should do next.

**Why this priority**: This is the core value proposition. Without
a working scan-and-explain pipeline, no other feature has meaning.

**Independent Test**: Can be fully tested by submitting sample emails
and verifying that every response contains a valid risk score,
classification, and human-readable explanation.

**Acceptance Scenarios**:

1. **Given** a raw email text and sender identifier, **When** the
   user submits the email for scanning, **Then** the system returns
   a risk score (integer 0-100), a classification (Safe, Suspicious,
   or Phishing), and a plain-English explanation.
2. **Given** a clearly legitimate email (e.g., known sender, no
   suspicious links, standard business content), **When** scanned,
   **Then** the system returns a risk score below 45 and classifies
   it as Safe with an explanation referencing the positive signals.
3. **Given** a clearly phishing email (e.g., spoofed sender, urgency
   language, malicious link patterns), **When** scanned, **Then** the
   system returns a risk score above 70 and classifies it as Phishing
   with an explanation identifying the threatening signals.
4. **Given** any scanned email, **When** the result is returned,
   **Then** the explanation includes: what the verdict is, why the
   decision was made, and what the user should do next.

---

### User Story 2 - LLM Escalation for Borderline Emails (Priority: P2)

When the ML classifier produces a borderline risk score
(approximately 45-70) or the email context is high-impact (finance,
HR, executive communications), the system automatically escalates
to an LLM for secondary review. The LLM refines the classification
reasoning and produces enhanced user guidance without blindly
overriding the ML score.

**Why this priority**: Borderline cases are where users need the
most help. LLM escalation adds value precisely where the ML model
is least certain, but it depends on the core pipeline (US1) working
first.

**Independent Test**: Can be tested by submitting emails that produce
borderline ML scores and verifying that LLM review is triggered, the
output includes enhanced reasoning, and the ML score is not blindly
overridden.

**Acceptance Scenarios**:

1. **Given** an email that produces an ML risk score between 45 and
   70, **When** the scan completes, **Then** the system triggers LLM
   review and the final output includes LLM-enhanced reasoning
   alongside the ML signals.
2. **Given** an email in a high-impact context (finance, HR, or
   executive communication), **When** the scan completes regardless
   of the ML score, **Then** the system triggers LLM review.
3. **Given** an email with an ML risk score below 45 and no
   high-impact context, **When** the scan completes, **Then** the
   system does NOT invoke the LLM.
4. **Given** an LLM escalation occurs, **When** the LLM suggests a
   refined verdict label that differs from the ML classification,
   **Then** the system logs both the ML and LLM outputs, the LLM
   references ML signals in its justification, and the ML risk
   score value remains unchanged.

---

### User Story 3 - Metric-Based Evaluation with Example Emails (Priority: P3)

The system supports evaluation against a curated set of example
emails (at least three: one safe, one phishing, one borderline).
Evaluation produces recall-prioritized metrics so operators can
assess detection quality and identify failure modes.

**Why this priority**: Evaluation ensures the system works
correctly and improves over time, but it is an operator-facing
capability that builds on top of the working scanner (US1) and
LLM escalation (US2).

**Independent Test**: Can be tested by running evaluation against
the example email set and verifying that recall, precision, and
per-email results are produced.

**Acceptance Scenarios**:

1. **Given** a curated set of at least three labeled example emails
   (safe, phishing, borderline), **When** the evaluation is run,
   **Then** the system produces per-email results (predicted vs.
   actual) and aggregate metrics including recall and precision.
2. **Given** the evaluation results, **When** a false negative
   occurs (phishing email classified as Safe), **Then** the system
   flags it prominently because recall is the priority metric.
3. **Given** the evaluation completes, **When** results are
   reviewed, **Then** failure modes (false negatives and false
   positives) are documented with the contributing signals that
   led to the misclassification.

---

### Edge Cases

- What happens when the email text is empty or contains only
  whitespace? The system MUST return an error indicating invalid
  input rather than producing a misleading classification.
- What happens when the sender identifier is missing or malformed?
  The system MUST still attempt classification using available
  signals and note the missing sender information in the
  explanation.
- What happens when the LLM service is unavailable during an
  escalation? The system MUST fall back to the ML-only result
  and indicate in the explanation that enhanced review was
  unavailable.
- What happens when an email contains no text body (attachments
  only)? The system MUST classify based on available metadata
  (sender, subject, attachment characteristics) and note the
  limited analysis scope in the explanation.
- What happens when the ML model produces a score exactly at a
  threshold boundary (e.g., exactly 45 or exactly 70)? The system
  MUST have deterministic boundary behavior (inclusive or exclusive)
  documented and consistently applied.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept raw email text and a sender
  identifier (string) as inputs for every scan.
- **FR-002**: System MUST produce three outputs for every scanned
  email: a risk score (integer 0-100), a classification (Safe,
  Suspicious, or Phishing), and a plain-English explanation.
- **FR-003**: The primary classification MUST be made by a
  lightweight, interpretable ML classifier that exposes its top
  contributing signals — defined as feature-level influences on
  the classification (e.g., "sender domain age", "urgency keyword
  count"), not raw model internals such as weights or coefficients.
- **FR-004**: Rule-based thresholds MUST map risk scores to
  classifications: scores below 45 are Safe, scores above 70
  are Phishing, scores between 45 and 70 (inclusive) are
  Suspicious. The risk score represents a probability-like
  confidence of phishing. Thresholds are configurable defaults
  and must remain explainable.
- **FR-005**: System MUST trigger LLM review when the ML risk score
  falls in the borderline range (45-70 inclusive) OR the email
  context is high-impact (finance, HR, executive communications).
- **FR-006**: The LLM MUST NOT change the ML risk score value.
  The LLM may suggest a refined verdict label but MUST reference
  the ML signals in its justification. Any LLM-driven label
  suggestion MUST be logged with rationale.
- **FR-007**: When the LLM is not invoked, the system MUST still
  produce a complete, valid output (score, classification,
  explanation) using ML signals alone.
- **FR-008**: Every explanation MUST answer three questions in
  plain English: (1) What is the verdict? (2) Why was this
  decision made? (3) What should the user do next?
- **FR-009**: Explanations MUST avoid technical jargon and
  reference the specific signals that drove the classification.
- **FR-010**: System MUST support metric-based evaluation against
  a curated set of labeled example emails (minimum three).
- **FR-011**: Evaluation metrics MUST include recall (primary)
  and precision (secondary), with false negatives flagged
  prominently.
- **FR-012**: System MUST handle invalid inputs (empty email,
  missing sender) gracefully with clear error messages rather
  than misleading classifications.
- **FR-013**: When the LLM service is unavailable during
  escalation, the system MUST fall back to ML-only results and
  note the limitation in the explanation.

### Key Entities

- **Email Submission**: The input to the scanner, consisting of
  raw email text and a sender identifier string. Represents a
  single email to be analyzed.
- **Scan Result**: The output of the scanner for a single email,
  containing: risk score (0-100), classification (Safe /
  Suspicious / Phishing), plain-English explanation, list of
  top contributing signals, and whether LLM escalation occurred.
- **Signal**: A feature-level influence on the classification
  identified by the ML model (e.g., "sender domain age", "urgency
  keyword count", "URL mismatch detected"). Each signal has a
  human-readable name, value, and contribution weight toward the
  risk score. Signals represent interpretable features, not raw
  model internals.
- **Evaluation Result**: The output of running the scanner against
  a labeled example set, containing per-email predictions vs.
  actuals and aggregate metrics (recall, precision).
- **Example Email**: A labeled email in the curated validation
  set, with known ground-truth classification used for evaluation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every scanned email produces all three required
  outputs (risk score, classification, explanation) with zero
  omissions.
- **SC-002**: Explanations are understandable by non-technical
  users — validated by confirming explanations contain no
  unexpanded technical jargon and answer all three required
  questions (verdict, reasoning, next steps).
- **SC-003**: The ML classifier exposes at least three contributing
  signals per prediction, each with a human-readable name.
- **SC-004**: LLM escalation is triggered for 100% of borderline
  scores (45-70) and high-impact contexts, and for 0% of
  non-borderline, non-high-impact emails.
- **SC-005**: The LLM never changes the ML risk score value, and
  any refined verdict label suggestion includes logged justification
  referencing ML signals — verified by audit log inspection.
- **SC-006**: When the LLM is unavailable, the system still
  produces a valid result within the same response structure.
- **SC-007**: Evaluation against the example set produces recall
  and precision metrics, with recall as the primary measure.
- **SC-008**: The system correctly classifies at least 2 out of 3
  example emails in the curated validation set (baseline for MVP).

## Assumptions

- The ML classifier will be trained or configured offline; this
  spec covers the scanning pipeline, not the training workflow.
  The dataset is used for model training and evaluation only.
- "High-impact context" detection (finance, HR, executive) will
  use keyword or metadata heuristics defined during implementation
  planning; the spec requires the capability without prescribing
  the detection method.
- The curated example email set (minimum three) will be created
  during implementation as test fixtures. Example emails may be
  synthetic or selected samples.
- Threshold values (45 and 70) are initial defaults and should be
  configurable without code changes. Thresholds are guideline-based
  and must remain explainable when adjusted.
