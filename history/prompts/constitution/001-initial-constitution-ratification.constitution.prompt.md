---
id: 001
title: Initial Constitution Ratification
stage: constitution
date: 2026-01-27
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: architect
command: /sp.constitution
labels: ["constitution", "governance", "principles", "phishing-scanner"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Project Goal:
Build an explainable phishing email scanner that prioritizes user trust, transparency, and controlled AI usage.

Core Principles:
- Explainability over maximum accuracy
- Deterministic ML decisions first, LLM second
- Clear, non-technical user explanations
- Modular, spec-driven architecture

Functional Rules:
- Every email must produce:
  - Risk score (0–100)
  - Classification: Safe / Suspicious / Phishing
  - Plain-English explanation
- ML model must expose top contributing signals
- LLM usage is strictly conditional:
  - Borderline risk scores (approx. 45–70)
  - High-impact contexts (finance, HR, executives)
- LLM must not blindly override ML outputs

Non-Functional Constraints:
- Use lightweight, interpretable ML models
- Avoid unnecessary complexity
- Ensure reproducibility and testability

Quality & Validation:
- Prefer recall-sensitive evaluation metrics
- Include example-driven validation
- Document failure modes and future improvements

## Response snapshot

Created constitution v1.0.0 for the Axioms Phishing Scanner project. Defined six core principles: (I) Explainability Over Accuracy, (II) Deterministic ML First LLM Second, (III) Clear Non-Technical Explanations, (IV) Modular Spec-Driven Architecture, (V) Recall-Sensitive Validation, (VI) Reproducibility and Testability. Added Functional Rules section codifying the three mandatory outputs (risk score, classification, explanation) and LLM invocation constraints. Added Non-Functional Constraints section covering model selection, complexity, reproducibility, and testability. Established governance with semantic versioning, amendment process, compliance review, and conflict resolution rules.

## Outcome

- Impact: Initial project constitution ratified at v1.0.0 with 6 principles, functional rules, non-functional constraints, and governance
- Tests: none (governance document)
- Files: .specify/memory/constitution.md (created/overwritten)
- Next prompts: /sp.specify to create the first feature spec; /sp.plan for implementation planning
- Reflection: User input was comprehensive; all principles mapped cleanly to constitution sections with no ambiguity requiring clarification

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS — no unresolved placeholders, all principles declarative and testable
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): validate constitution gates during first /sp.plan run
