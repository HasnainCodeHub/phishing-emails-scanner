# Tasks: Explainable Phishing Email Scanner

**Input**: Design documents from `/specs/001-phishing-email-scanner/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Explicitly requested by user. Unit tests for each core module plus integration tests for full pipeline.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Python project with UV, declare all dependencies, create directory structure

- [x] T001 Create project directory structure per plan.md (src/, tests/, data/, notebooks/ with all subdirectories and __init__.py files)
- [x] T002 Initialize Python project with UV: run `uv init`, set Python >=3.13 in pyproject.toml, add dependencies (scikit-learn, openai-agents, joblib) and dev dependencies (pytest, jupyter)
- [x] T003 [P] Create .gitignore with entries for data/model/*.joblib, data/training/, .env, __pycache__/, .venv/, *.pyc
- [x] T004 [P] Create .env.example with all SCANNER_* environment variables and OPENAI_API_KEY placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, configuration, and shared infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement configuration module in src/config.py — externalize all thresholds (SAFE_THRESHOLD=45, PHISHING_THRESHOLD=70), model paths (MODEL_PATH=data/model/classifier.joblib), LLM settings (LLM_ENABLED=true, LLM_MODEL=gpt-4o-mini), and RANDOM_SEED=42 with environment variable overrides (SCANNER_* prefix). Use dataclass or simple module-level constants.
- [x] T006 [P] Implement Signal dataclass in src/models/signal.py — fields: name (str), display_name (str), value (float|int|bool), weight (float). Per data-model.md. Include __repr__ for debugging.
- [x] T007 [P] Implement EmailSubmission dataclass in src/models/email_submission.py — fields: email_text (str), sender (str). Include validation: email_text must not be empty/whitespace. Per data-model.md.
- [x] T008 [P] Implement ScanResult dataclass in src/models/scan_result.py — fields: risk_score (int 0-100), classification (str: Safe|Suspicious|Phishing), explanation (str), signals (list[Signal]), llm_escalated (bool), llm_output (LLMReviewResult|None). Per data-model.md.
- [x] T009 [P] Implement LLMReviewResult dataclass in src/models/scan_result.py — fields: llm_explanation (str), suggested_label (str|None), rationale (str), prompt_log (str), response_log (str). Per data-model.md.
- [x] T010 [P] Create shared test fixtures in tests/conftest.py — define pytest fixtures for: sample safe email text+sender, sample phishing email text+sender, sample borderline email text+sender, sample feature dictionaries, mock Signal objects. These fixtures are used by all test phases.
- [x] T011 [P] Create curated example emails JSON fixture in tests/fixtures/example_emails.json — minimum 3 labeled emails: one Safe (legitimate business email from known sender), one Phishing (spoofed sender, urgency keywords, suspicious URLs), one Borderline/Suspicious (ambiguous content, financial context). Each entry: id, email_text, sender, label, description. Per ExampleEmail entity in data-model.md.

**Checkpoint**: Foundation ready — all data models, config, and fixtures available for user story implementation

---

## Phase 3: User Story 1 — Scan an Email and Get a Verdict (Priority: P1) MVP

**Goal**: User submits raw email text + sender → system returns risk score (0-100), classification (Safe/Suspicious/Phishing), and plain-English explanation with top contributing signals

**Independent Test**: Submit sample emails and verify every response contains valid risk score, classification, and human-readable explanation answering: verdict, reasoning, next steps

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T012 [P] [US1] Unit test for feature extractor in tests/unit/test_extractor.py — test extract_features() with: safe email (low urgency, no suspicious URLs), phishing email (high urgency, suspicious URLs, sender mismatch), empty email (expect ValueError), missing sender (should still extract features). Verify output is dict[str, float|int|bool] with expected feature keys. Per contract in scanner-api.md §1.
- [x] T013 [P] [US1] Unit test for ML classifier in tests/unit/test_classifier.py — test PhishingClassifier.predict() with: mock model returning known probabilities, verify risk_score is int 0-100, verify signals list has >=3 items sorted by absolute weight, verify Signal objects have name/display_name/value/weight. Test train() saves model to disk. Per contract in scanner-api.md §2.
- [x] T014 [P] [US1] Unit test for rule engine in tests/unit/test_rules.py — test classify() with: score=30 → ("Safe", False, False), score=55 → ("Suspicious", True, False), score=85 → ("Phishing", False, False), score=45 → ("Suspicious", True, *), score=70 → ("Suspicious", True, *), high-impact features → (*, *, True). Test configurable thresholds. Per contract in scanner-api.md §3.
- [x] T015 [P] [US1] Unit test for explanation generator in tests/unit/test_generator.py — test generate_explanation() with: Safe classification + signals → explanation contains verdict/reasoning/next steps, Phishing classification → explanation references signal display names, no technical jargon in output. Test with and without LLM output. Per contract in scanner-api.md §5.
- [x] T016 [P] [US1] Integration test for ML-only pipeline in tests/integration/test_pipeline.py — test EmailScanner.scan() end-to-end without LLM: submit safe email → verify ScanResult has score <45, classification "Safe", non-empty explanation. Submit phishing email → verify score >70, classification "Phishing". Submit empty email → expect ValueError. Verify llm_escalated=False for clear safe/phishing cases.

### Implementation for User Story 1

- [x] T017 [US1] Implement feature extraction in src/features/extractor.py — function extract_features(email_text, sender) → dict. Extract features: urgency_keyword_count (regex for "urgent", "immediately", "act now", "expire", "verify your", "suspended"), url_count (regex URL pattern), has_suspicious_url (non-standard TLDs, IP-based URLs), sender_domain_mismatch (sender domain vs. email body domain references), financial_keyword_count ("invoice", "payment", "wire transfer", "bank account", "tax", "billing"), has_attachment_reference ("attached", "attachment", "see attached"), is_high_impact_context (True if financial_keyword_count>0 OR hr_keyword_count>0 OR executive_keyword_count>0), executive_keyword_count ("CEO", "CFO", "board", "confidential"), hr_keyword_count ("benefits", "payroll", "salary", "termination", "offer letter"). Raise ValueError on empty/whitespace email_text. Per contract in scanner-api.md §1.
- [x] T018 [US1] Implement ML classifier wrapper in src/scoring/classifier.py — class PhishingClassifier with: __init__(model_path) loads joblib model, predict(features) → (risk_score, signals) using predict_proba * 100 rounded, signals from model coefficients mapped to feature names with display_name and weight sorted by abs(weight) descending. Class method train(X, y, model_path, seed=42) trains LogisticRegression(random_state=seed, max_iter=1000) with DictVectorizer, saves with joblib. Per contract in scanner-api.md §2 and research.md R1.
- [x] T019 [US1] Implement rule-based classification in src/decision/rules.py — function classify(risk_score, features, safe_threshold=45, phishing_threshold=70) → (classification, is_borderline, is_high_impact). Boundary: score < safe_threshold → "Safe", score > phishing_threshold → "Phishing", else → "Suspicious". is_borderline = safe_threshold <= score <= phishing_threshold. is_high_impact from features["is_high_impact_context"]. Per contract in scanner-api.md §3.
- [x] T020 [US1] Implement explanation generator in src/explanation/generator.py — function generate_explanation(classification, signals, llm_output=None) → str. Template-based: map each signal.name to plain-English template (e.g., urgency_keyword_count → "This email uses urgent language {value} times, which is common in phishing attempts."). Structure output: (1) verdict sentence, (2) bullet list of signal explanations, (3) recommended next action. If llm_output provided, append LLM reasoning section. No technical jargon. Per contract in scanner-api.md §5 and research.md R5.
- [x] T021 [US1] Implement pipeline orchestrator in src/pipeline/scanner.py — class EmailScanner with __init__(config) loading model, async scan(email_text, sender) → ScanResult executing: validate input → extract features → classify with ML → apply rules → check escalation triggers → generate explanation → return ScanResult. For US1, LLM escalation branch returns llm_escalated=False, llm_output=None (placeholder for US2). Per contract in scanner-api.md §6.
- [x] T022 [US1] Implement CLI entry point in src/cli.py — commands: `scan --email TEXT --sender SENDER` or `scan --file PATH --sender SENDER`, `evaluate` (placeholder for US3), `train` (delegates to classifier.train). Output formatted ScanResult to stdout. Use argparse.
- [x] T023 [US1] Prepare training data and train initial model — create or download a small phishing dataset in data/training/ (CSV with email_text, sender, label columns). Run feature extraction on training data, train LogisticRegression via PhishingClassifier.train(), save model to data/model/classifier.joblib. Document dataset source and size. Verify model produces reasonable scores on the 3 example emails from fixtures.

**Checkpoint**: User Story 1 complete — ML-only scan pipeline works end-to-end. Users can submit emails and get risk score + classification + explanation. LLM escalation not yet wired.

---

## Phase 4: User Story 2 — LLM Escalation for Borderline Emails (Priority: P2)

**Goal**: Emails with borderline scores (45-70) or high-impact context automatically escalate to LLM for secondary review. LLM enhances explanation without modifying ML risk score.

**Independent Test**: Submit borderline-score emails → verify LLM is triggered and output includes enhanced reasoning. Submit clear safe/phishing emails → verify LLM is NOT triggered. Verify ML risk score is unchanged after LLM review.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [P] [US2] Unit test for LLM escalation agent in tests/unit/test_llm_agent.py — test escalate() with mocked OpenAI agent: verify LLMReviewResult contains non-empty llm_explanation, rationale references at least one ML signal name, prompt_log and response_log are populated. Test LLMUnavailableError is raised when agent unreachable. Per contract in scanner-api.md §4.
- [x] T025 [P] [US2] Integration test for pipeline with LLM in tests/integration/test_pipeline_llm.py — test EmailScanner.scan() with mocked LLM: submit borderline email (score 45-70) → verify llm_escalated=True, llm_output is not None, risk_score unchanged from ML output. Submit high-impact email → verify LLM triggered regardless of score. Submit safe email (score <45, no high-impact) → verify llm_escalated=False. Test LLM unavailable fallback → verify valid ScanResult with llm_escalated=False and explanation notes fallback.

### Implementation for User Story 2

- [x] T026 [US2] Implement LLM escalation agent in src/escalation/llm_agent.py — async function escalate(email_text, sender, risk_score, classification, signals) → LLMReviewResult. Use OpenAI Agents SDK: define single agent with system prompt instructing it to review borderline email, reference ML signals by name, produce plain-English reasoning and user guidance, optionally suggest a refined verdict label. Truncate email_text to 2000 chars. Log full prompt and response in LLMReviewResult.prompt_log/.response_log. Define LLMUnavailableError exception. Per contract in scanner-api.md §4 and research.md R2.
- [ ] T027 [US2] Wire LLM escalation into pipeline in src/pipeline/scanner.py — update EmailScanner.scan() to: after rule classification, check if is_borderline OR is_high_impact → if True and LLM_ENABLED → try escalate(), catch LLMUnavailableError and fall back to ML-only with explanation noting fallback. Pass LLM output to explanation generator. ML risk_score MUST remain unchanged. Per FR-005, FR-006, FR-007, FR-013.
- [x] T028 [US2] Update explanation generator in src/explanation/generator.py — enhance generate_explanation() to integrate LLM output when provided: append "Enhanced Review" section with llm_explanation, note if LLM suggested a different verdict label (with logged rationale), include LLM-generated user guidance. When LLM was unavailable, add note: "Enhanced review was unavailable; this analysis is based on automated signals only."

**Checkpoint**: User Story 2 complete — borderline and high-impact emails get LLM-enhanced explanations. ML score never modified. LLM fallback works gracefully.

---

## Phase 5: User Story 3 — Metric-Based Evaluation with Example Emails (Priority: P3)

**Goal**: Evaluate scanner against curated example emails, produce recall (primary), precision (secondary), F1 metrics, and per-email results with failure mode documentation.

**Independent Test**: Run evaluation against example email set → verify recall, precision, F1 metrics produced, per-email results list failure modes with contributing signals.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T029 [P] [US3] Unit test for evaluator in tests/unit/test_evaluator.py — test evaluate() with mock scanner returning known ScanResults for the 3 example emails: verify EvaluationResult has recall, precision, f1 as floats in [0,1], per_email has >=3 entries each with predicted/actual/risk_score/correct/signals. Test false negative flagging. Per contract in scanner-api.md §7.

### Implementation for User Story 3

- [x] T030 [P] [US3] Implement EvaluationResult and EmailEvaluation dataclasses in src/models/scan_result.py — EvaluationResult: recall (float), precision (float), f1 (float), per_email (list[EmailEvaluation]). EmailEvaluation: email_id (str), predicted (str), actual (str), risk_score (int), correct (bool), signals (list[Signal]). Per data-model.md.
- [x] T031 [US3] Implement evaluator in src/evaluation/evaluator.py — async function evaluate(scanner, examples) → EvaluationResult. For each ExampleEmail: run scanner.scan(), compare predicted classification to label, collect per-email results. Compute metrics using scikit-learn: recall_score, precision_score, f1_score with pos_label="Phishing". Flag false negatives prominently in output. Per contract in scanner-api.md §7 and FR-010, FR-011.
- [x] T032 [US3] Wire evaluate command into CLI in src/cli.py — implement `evaluate` subcommand: load example_emails.json from fixtures, initialize scanner, run evaluator, print formatted results table (per-email) and aggregate metrics with recall highlighted as primary. Document metric choice rationale in output header.
- [x] T033 [US3] Implement ExampleEmail loader in src/evaluation/evaluator.py — function load_examples(path) → list[ExampleEmail] that reads tests/fixtures/example_emails.json and returns typed ExampleEmail objects. Validate minimum 3 entries.

**Checkpoint**: User Story 3 complete — evaluation produces recall-prioritized metrics, per-email breakdown, and failure mode documentation.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Demo interface, documentation, and final validation

- [x] T034 [P] Create Jupyter demo notebook in notebooks/demo.ipynb — demonstrate end-to-end usage: (1) scan a safe email, (2) scan a phishing email, (3) scan a borderline email triggering LLM escalation, (4) run evaluation. Show formatted outputs for each. Include markdown cells explaining architecture and design decisions.
- [x] T035 [P] Generate README.md at repository root — document: project overview, architecture diagram (text-based pipeline from plan.md), design decisions (from research.md: classifier choice, LLM integration, explanation strategy), setup instructions (from quickstart.md), usage examples, failure modes (LLM unavailable fallback, empty input handling, threshold boundary behavior), future improvements (NLP features, model ensemble with explanation wrapper, real-time email integration).
- [x] T036 Run quickstart.md validation — follow quickstart.md steps end-to-end on a clean environment: uv sync, train model, scan example emails via CLI, run evaluation, run pytest. Document any discrepancies and fix.
- [x] T037 Run full test suite and verify all tests pass — execute `uv run pytest` and ensure: all unit tests pass (6 test files), all integration tests pass (2 test files), example email fixtures produce expected classification ranges.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (needs working pipeline to wire LLM into)
- **User Story 3 (Phase 5)**: Depends on User Story 1 completion (needs working scanner for evaluation). Can run in parallel with US2.
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 pipeline being functional — adds LLM escalation branch to existing pipeline
- **User Story 3 (P3)**: Depends on US1 scanner being functional — evaluates against it. Independent of US2 (can evaluate ML-only pipeline)

### Within Each User Story

- Tests MUST be written FIRST and FAIL before implementation
- Models before services
- Services before pipeline integration
- Core implementation before CLI wiring

### Parallel Opportunities

- **Phase 1**: T003 and T004 can run in parallel
- **Phase 2**: T006, T007, T008, T009, T010, T011 can all run in parallel (different files)
- **Phase 3 Tests**: T012, T013, T014, T015, T016 can all run in parallel
- **Phase 3 Implementation**: T017, T018, T019, T020 can run in parallel (different modules), then T021 (depends on all four), then T022, T023
- **Phase 4 Tests**: T024, T025 can run in parallel
- **Phase 5 Tests + Impl**: T029 and T030 can run in parallel
- **Phase 6**: T034 and T035 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (write first, expect failures):
Task: "Unit test for feature extractor in tests/unit/test_extractor.py"
Task: "Unit test for ML classifier in tests/unit/test_classifier.py"
Task: "Unit test for rule engine in tests/unit/test_rules.py"
Task: "Unit test for explanation generator in tests/unit/test_generator.py"
Task: "Integration test for ML-only pipeline in tests/integration/test_pipeline.py"

# Launch parallel implementation modules:
Task: "Implement feature extraction in src/features/extractor.py"
Task: "Implement ML classifier wrapper in src/scoring/classifier.py"
Task: "Implement rule-based classification in src/decision/rules.py"
Task: "Implement explanation generator in src/explanation/generator.py"

# Then sequential (depends on above):
Task: "Implement pipeline orchestrator in src/pipeline/scanner.py"
Task: "Implement CLI entry point in src/cli.py"
Task: "Prepare training data and train initial model"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test US1 independently — scan emails via CLI and verify outputs
5. Demo-ready at this point (ML-only pipeline)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (MVP!)
3. Add User Story 2 → Test independently → Demo (LLM-enhanced)
4. Add User Story 3 → Test independently → Demo (evaluation metrics)
5. Polish → README, notebook, final validation
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (must complete first)
3. Once US1 is done:
   - Developer A: User Story 2
   - Developer B: User Story 3 (parallel with US2)
4. All developers: Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests written FIRST, expected to FAIL, then implementation makes them pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- US2 depends on US1 because it modifies the pipeline orchestrator
- US3 can run in parallel with US2 since it only needs the ML-only scanner
