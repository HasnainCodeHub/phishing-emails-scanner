---
id: 003
title: Implementation Plan Phishing Scanner
stage: plan
date: 2026-01-27
surface: agent
model: claude-opus-4-5-20251101
feature: 001-phishing-email-scanner
branch: 001-phishing-email-scanner
user: architect
command: /sp.plan
labels: ["plan", "architecture", "ml-pipeline", "scikit-learn", "openai-agents-sdk"]
links:
  spec: specs/001-phishing-email-scanner/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phishing-email-scanner/plan.md
  - specs/001-phishing-email-scanner/research.md
  - specs/001-phishing-email-scanner/data-model.md
  - specs/001-phishing-email-scanner/quickstart.md
  - specs/001-phishing-email-scanner/contracts/scanner-api.md
tests:
  - none
---

## Prompt

/sp.plan

Implement the system using the following architecture and stack:

Language & Runtime:
- Python 3.13+
- UV for dependency and environment management

Core Processing Layers:
1. Feature Extraction:
   - Pure Python + regex for text signal extraction
2. ML Scoring Layer:
   - scikit-learn with a lightweight, interpretable classifier
   - Outputs risk score (0–100) and top contributing features
3. Rule-Based Decision Layer:
   - Deterministic threshold logic for Safe / Phishing / Borderline
4. LLM Escalation Layer (conditional only):
   - OpenAI Agents SDK (Python)
   - Single agent for borderline review and explanation
   - LLM must not modify ML risk score

Supporting Components:
- Evaluation & Metrics:
  - scikit-learn metrics (precision, recall, F1)
- Testing:
  - pytest for unit and integration tests
- Interface:
  - Jupyter Notebook or simple Python CLI for demonstration
- Documentation:
  - Markdown (README)

Constraints:
- No end-to-end LLM classification
- LLM invoked only via explicit escalation rules
- Emphasize explainability, modularity, and reproducibility

## Response snapshot

Created full implementation plan with 5 artifacts. Plan defines a 6-layer processing pipeline (Feature Extraction → ML Scoring → Rule Engine → Escalation Check → Explanation Generator → Scan Result) using Python 3.13+, scikit-learn LogisticRegression, and OpenAI Agents SDK. All 6 constitution gates pass. Research resolved 5 decisions: LogisticRegression over alternatives, OpenAI Agents SDK single-agent pattern, regex-based feature extraction, UV for dependency management, and template-based explanation generation. Data model defines 7 entities (EmailSubmission, Signal, ScanResult, LLMReviewResult, EvaluationResult, EmailEvaluation, ExampleEmail) with 6 configuration parameters. Contracts define 7 module interfaces with Python function signatures. Quickstart covers setup, training, scanning, evaluation, and testing workflows.

## Outcome

- Impact: Complete implementation plan with architecture, research, data model, contracts, and quickstart ready for task generation
- Tests: none (planning phase)
- Files: plan.md, research.md, data-model.md, quickstart.md, contracts/scanner-api.md
- Next prompts: /sp.tasks to generate implementation tasks; /sp.adr if architectural decisions warrant formal ADR
- Reflection: User input was comprehensive with explicit stack choices; no NEEDS CLARIFICATION items. Constitution check passed all 6 gates cleanly.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): constitution check PASS (6/6 gates), all technical context resolved
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): validate contracts during /sp.tasks by cross-referencing task file paths with plan structure
