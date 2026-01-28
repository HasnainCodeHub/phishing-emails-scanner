# Explainable Phishing Email Scanner

### ML Classification + Controlled LLM Escalation

---

## 1. Problem Statement

Phishing emails remain one of the top cybersecurity threats. Existing spam filters often work as black boxes — users don't know **why** an email was flagged. This project solves two problems:

1. **Detection** — Classify emails as Safe, Suspicious, or Phishing using ML.
2. **Explainability** — Tell the user *why* the decision was made in plain English, with no technical jargon.

---

## 2. Solution Overview

A hybrid system that combines:

- **Machine Learning (Logistic Regression)** for fast, deterministic classification
- **LLM (Gemini 2.5 Flash)** for deeper analysis of borderline/high-impact emails
- **Plain-English Explanations** so any user can understand the result

```
Email Input
    |
    v
[Feature Extraction] ── 9 hand-crafted features via regex
    |
    v
[ML Classifier] ── Logistic Regression → Risk Score (0-100)
    |
    v
[Rule Engine] ── Safe (<45) | Suspicious (45-70) | Phishing (>70)
    |
    v
[Escalation Check] ── Borderline OR High-Impact?
    |                        |
    No                      Yes + LLM Enabled
    |                        |
    v                        v
[Explanation]          [LLM Review (Gemini)]
    |                        |
    v                        v
         Final Output
```

---

## 3. Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.13+ | Core runtime |
| ML Classifier | scikit-learn (Logistic Regression) | Email scoring & signal extraction |
| LLM Agent | openai-agents SDK + Gemini 2.5 Flash | Secondary review for borderline emails |
| Model Storage | joblib | Serialize/load trained model |
| Dataset | Kaggle (82,485 samples) | Training data |
| Testing | pytest + pytest-asyncio | 50 unit & integration tests |
| Config | python-dotenv | Environment-based configuration |

---

## 4. Feature Extraction (9 Features)

The system extracts **9 features** from every email using regex pattern matching:

| # | Feature | Type | What It Detects |
|---|---------|------|-----------------|
| 1 | `urgency_keyword_count` | int | "urgent", "immediately", "act now", "verify your", "suspended", "within X hours" |
| 2 | `url_count` | int | Total number of embedded URLs |
| 3 | `has_suspicious_url` | bool | IP-based URLs or suspicious TLDs (.xyz, .tk, .ml, etc.) |
| 4 | `sender_domain_mismatch` | bool | Sender's domain differs from URL domains in the body |
| 5 | `financial_keyword_count` | int | "invoice", "payment", "wire transfer", "bank account" |
| 6 | `has_attachment_reference` | bool | "attached", "find attached", "see attached" |
| 7 | `is_high_impact_context` | bool | True if financial, HR, or executive keywords present |
| 8 | `executive_keyword_count` | int | "ceo", "cfo", "board", "confidential" |
| 9 | `hr_keyword_count` | int | "payroll", "salary", "benefits", "termination" |

---

## 5. ML Classifier

**Algorithm:** Logistic Regression (scikit-learn)

**Why Logistic Regression?**
- Produces probability scores (0-100%) — not just yes/no
- Coefficients are directly interpretable as feature weights
- Fast inference — suitable for real-time scanning
- Deterministic — same email always gets the same score

**Pipeline:**
```
DictVectorizer → LogisticRegression(max_iter=1000, solver='lbfgs', random_state=42)
```

**Training Data:** Kaggle Phishing Email Dataset — **82,485 labeled samples**

**How Scoring Works:**
1. Extract 9 features from the email
2. Feed features into the trained model
3. Get phishing probability → multiply by 100 → **Risk Score**
4. Extract model coefficients → map to features → **Signals** (sorted by weight)

---

## 6. Classification Rules

The risk score is mapped to a verdict using configurable thresholds:

```
  0 ─────────── 44    →  Safe
 45 ─────────── 70    →  Suspicious (Borderline)
 71 ────────── 100    →  Phishing
```

| Classification | Risk Score Range | Action |
|---------------|-----------------|--------|
| **Safe** | 0 – 44 | No action needed |
| **Suspicious** | 45 – 70 | Caution — verify sender |
| **Phishing** | 71 – 100 | Do not click — report to IT |

---

## 7. LLM Escalation (Controlled)

Not every email goes to the LLM. Escalation is **conditional**:

**Trigger Conditions:**
```
Escalate = (Borderline Score [45-70] OR High-Impact Context) AND LLM Enabled
```

**High-Impact Context** means the email involves:
- Financial topics (invoices, payments, bank accounts)
- HR topics (payroll, salary, benefits)
- Executive topics (CEO, CFO, board, confidential)

**LLM Integration:**
- **Provider:** Google Gemini via OpenAI-compatible API
- **Model:** gemini-2.5-flash
- **Framework:** openai-agents SDK (Agent + Runner pattern)
- **Input:** Email text (truncated to 2000 chars) + ML signals + risk score
- **Output:** Detailed analysis + phishing indicators + recommendations

**Key Constraint:** The LLM **cannot change the ML risk score**. It provides additional analysis only.

**Fallback:** If the LLM is unavailable, the system gracefully falls back to ML-only output.

---

## 8. Output Format

```
Final Verdict: Phishing
Risk Score: 88%

ML Analysis:
  • High urgency phrases detected (3 found)
  • High-impact context (financial, HR, or executive)

LLM Review:
  This email exhibits classic phishing characteristics including
  urgency tactics, suspicious sender domain, and a malicious link...

User Guidance:
  Do not click any links or provide information.
  Report this email to IT/security.
  Delete the email after reporting.
```

The output has **5 sections**:
1. **Final Verdict** — Safe / Suspicious / Phishing
2. **Risk Score** — Percentage (0-100%)
3. **ML Analysis** — Top contributing signals in plain English
4. **LLM Review** — Detailed analysis (only when escalated)
5. **User Guidance** — Actionable next steps

---

## 9. Sample Results

### Safe Email
```
From: sarah@company.com
Body: "Hi John, please find the quarterly report attached..."

Final Verdict: Safe
Risk Score: 15%

ML Analysis:
  • Attachment reference detected
  • High urgency phrases detected (0 found)

User Guidance:
  No immediate action is needed. This email appears legitimate.
```

### Phishing Email
```
From: security@bank-alerts.com
Body: "URGENT: Your bank account has been compromised! Click here..."

Final Verdict: Phishing
Risk Score: 88%

ML Analysis:
  • High urgency phrases detected (3 found)
  • High-impact context (financial, HR, or executive)

LLM Review:
  This email is highly suspicious. The sender domain "bank-alerts.com"
  is not a legitimate bank domain. Phrases like "URGENT" and "locked
  in 24 hours" are classic social engineering tactics. The URL
  "http://suspicious-site.com/verify" is clearly malicious.

User Guidance:
  Do not click any links or provide information.
  Report this email to IT/security.
  Delete the email after reporting.

[LLM Escalation: Triggered]
```

### Borderline / Suspicious Email
```
From: hr@company.com
Body: "Dear employee, please update your payroll bank account details..."

Final Verdict: Suspicious
Risk Score: 48%

ML Analysis:
  • HR-related topics detected (1 found)
  • High-impact context (financial, HR, or executive)

LLM Review:
  This email appears suspicious despite the seemingly legitimate sender.
  The generic greeting "Dear employee", the request for bank details
  via a link, and the phrase "routine verification process" are common
  social engineering tactics.

User Guidance:
  Exercise caution with this email.
  Avoid clicking links or downloading attachments until you verify the sender.
  Report to IT/security if uncertain.

[LLM Escalation: Triggered]
```

---

## 10. Evaluation Metrics

**Primary Metric: Recall** — Because missing a phishing email (false negative) is more dangerous than a false alarm.

| Metric | Score |
|--------|-------|
| **Recall** | 1.000 |
| **Precision** | 1.000 |
| **F1 Score** | 1.000 |

Trained on **82,485 samples** from the Kaggle Phishing Email Dataset.

---

## 11. Project Architecture

```
axioms-task/
├── main.py                          # Demo entry point
├── pyproject.toml                   # Dependencies & config
├── .env.example                     # Environment template
│
├── src/
│   ├── config.py                    # ScannerConfig (thresholds, paths)
│   ├── cli.py                       # CLI commands (scan, train, evaluate)
│   ├── features/
│   │   └── extractor.py             # 9-feature regex extraction
│   ├── scoring/
│   │   └── classifier.py            # Logistic Regression wrapper
│   ├── decision/
│   │   └── rules.py                 # Threshold-based classification
│   ├── escalation/
│   │   └── llm_agent.py             # Gemini LLM integration
│   ├── explanation/
│   │   └── generator.py             # Plain-English output builder
│   ├── pipeline/
│   │   └── scanner.py               # Pipeline orchestrator
│   ├── evaluation/
│   │   └── evaluator.py             # Recall/Precision/F1 computation
│   └── models/
│       ├── signal.py                # Signal dataclass
│       └── scan_result.py           # ScanResult, LLMReviewResult
│
├── tests/
│   ├── unit/                        # 6 unit test modules
│   ├── integration/                 # 2 integration test modules
│   ├── conftest.py                  # Shared fixtures
│   └── fixtures/
│       └── example_emails.json      # 3 labeled test emails
│
└── data/
    ├── model/classifier.joblib      # Trained model artifact
    └── training/                    # Kaggle dataset (auto-downloaded)
```

---

## 12. How to Run

**Setup:**
```bash
# Install dependencies
uv sync

# Set Gemini API key
cp .env.example .env
# Edit .env → GEMINI_API_KEY=your_key_here
```

**Commands:**
```bash
# Run the demo (3 test emails)
uv run python main.py

# Scan a specific email
uv run python -m src.cli scan --email "Suspicious email text..." --sender "sender@example.com"

# Train the model (auto-downloads Kaggle dataset)
uv run python -m src.cli train

# Evaluate model performance
uv run python -m src.cli evaluate

# Run all 50 tests
uv run pytest tests/ -v
```

---

## 13. Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ML Algorithm | Logistic Regression | Interpretable coefficients = explainable signals |
| LLM Trigger | Conditional (not every email) | Cost control + only where ML is uncertain |
| LLM Provider | Gemini 2.5 Flash | Fast, cost-effective, OpenAI-compatible API |
| Score Preservation | LLM cannot modify ML score | Determinism — ML is the source of truth |
| Primary Metric | Recall over Precision | Missing phishing is worse than false alarms |
| Feature Extraction | Regex (no NLP models) | Lightweight, fast, no external dependencies |
| Explanation Style | Template-based + LLM augmentation | Consistent format with depth when needed |

---

## 14. Error Handling

| Scenario | Behavior |
|----------|----------|
| Empty email input | ValueError raised — clear error message |
| Model file missing | ModelNotFoundError — prompts to train first |
| LLM API unavailable | Graceful fallback to ML-only explanation |
| Invalid risk score | ValueError — must be 0-100 |
| Invalid classification | ValueError — must be Safe/Suspicious/Phishing |

---

## 15. Testing Summary

**50 tests** across 8 test files — all passing.

| Category | Tests | What's Covered |
|----------|-------|---------------|
| Feature Extraction | 8 | Safe/phishing features, edge cases, data types |
| ML Classifier | 6 | Scoring, signal sorting, model persistence |
| Classification Rules | 10 | Threshold boundaries, borderline detection |
| Explanation Generator | 7 | Format, templates, LLM integration, no jargon |
| LLM Agent | 5 | Escalation triggers, mocking, fallback |
| Evaluator | 4 | Metrics computation, per-email tracking |
| Pipeline Integration | 5 | Full scan flow, field validation |
| Pipeline + LLM | 5 | Escalation triggers, fallback, score preservation |

---

## 16. Key Takeaways

1. **ML-first, LLM-second** — Logistic Regression handles 100% of emails; LLM only reviews borderline/high-impact cases
2. **Explainability built-in** — Every decision is traceable to specific features and weights
3. **No black box** — Users see exactly which signals triggered the classification
4. **Cost-efficient** — LLM calls only when genuinely needed (conditional escalation)
5. **Production-ready patterns** — Async pipeline, graceful fallback, full test coverage, configurable thresholds
