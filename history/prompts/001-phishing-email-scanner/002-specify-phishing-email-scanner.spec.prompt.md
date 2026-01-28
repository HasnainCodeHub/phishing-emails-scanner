---
id: 002
title: Specify Phishing Email Scanner
stage: spec
date: 2026-01-27
surface: agent
model: claude-opus-4-5-20251101
feature: 001-phishing-email-scanner
branch: 001-phishing-email-scanner
user: architect
command: /sp.specify
labels: ["spec", "phishing-scanner", "ml-classification", "llm-escalation", "explainability"]
links:
  spec: specs/001-phishing-email-scanner/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phishing-email-scanner/spec.md
  - specs/001-phishing-email-scanner/checklists/requirements.md
tests:
  - none
---

## Prompt

/sp.specify

Specify an explainable phishing email scanning system with the following behavior:

Inputs:
- Raw email text
- Sender identifier (string)

Core Outputs (required for every email):
- Risk score between 0 and 100
- Classification: Safe, Suspicious, or Phishing
- Plain-English explanation suitable for non-technical users

Decision Logic:
- Primary decision must be made using a lightweight, interpretable ML classifier
- ML output must expose top contributing signals for explainability
- Rule-based thresholds determine Safe / Phishing / Borderline outcomes

LLM Escalation (conditional only):
- Trigger LLM review only when:
  - Risk score is borderline (approximately 45–70), OR
  - Email context is high-impact (finance, HR, executives)
- LLM responsibilities:
  - Review borderline classification
  - Summarize reasoning in simple language
  - Provide user guidance
- LLM must not blindly override ML risk score

Explainability Requirements:
- Every decision must clearly answer:
  - What is the verdict?
  - Why was this decision made?
  - What should the user do next?

Validation & Evaluation:
- System must support metric-based evaluation
- Metrics should prioritize phishing-appropriate tradeoffs (e.g., recall)
- Include example-driven analysis for at least three emails

Constraints:
- Avoid end-to-end LLM classification
- Favor simplicity, transparency, and reproducibility

## Response snapshot

Created feature branch `001-phishing-email-scanner` and wrote spec.md with three user stories: (P1) Scan an Email and Get a Verdict — core ML pipeline producing risk score, classification, and plain-English explanation; (P2) LLM Escalation for Borderline Emails — conditional LLM review for scores 45-70 or high-impact contexts with no blind override; (P3) Metric-Based Evaluation with Example Emails — recall-prioritized evaluation against curated example set. Defined 13 functional requirements (FR-001 through FR-013), 5 key entities, 8 success criteria, 5 edge cases, and 4 documented assumptions. Quality checklist passed all items with zero NEEDS CLARIFICATION markers.

## Outcome

- Impact: Feature specification created with full coverage of ML classification, LLM escalation, explainability, and evaluation requirements
- Tests: none (specification document)
- Files: specs/001-phishing-email-scanner/spec.md, specs/001-phishing-email-scanner/checklists/requirements.md
- Next prompts: /sp.clarify to refine ambiguities, or /sp.plan to begin implementation planning
- Reflection: User description was comprehensive; no clarification needed. All requirements mapped directly from user input to testable functional requirements.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): quality checklist PASS — all 16 items verified
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): run /sp.clarify to stress-test spec completeness before planning
