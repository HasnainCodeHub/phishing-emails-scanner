# Expected Interview Questions

## 1. Project Overview

**Q: What is this project about?**
A: It is an Explainable Phishing Email Scanner that uses a two-layer approach: a primary ML classifier (Logistic Regression) that scores emails 0-100 for phishing risk, and a secondary LLM layer (Google Gemini) that is conditionally triggered for borderline or high-impact emails. The system produces plain-English explanations so non-technical users can understand why an email was flagged.

**Q: Why did you build this project?**
A: To demonstrate how ML and LLM can work together in a controlled, explainable way for email security. The ML model handles the bulk of classification efficiently, while the LLM provides deeper analysis only when needed, keeping costs low and responses fast.

**Q: What problem does this project solve?**
A: Traditional spam filters are black boxes. Users don't know why an email was flagged. This scanner provides transparent, explainable verdicts with specific signal breakdowns and human-readable recommendations.

---

## 2. Architecture & Design

**Q: Explain the full pipeline flow.**
A: The pipeline has 6 steps:
1. **Feature Extraction** - Regex-based extraction of 9 signals from email text (urgency keywords, URLs, sender mismatch, financial/HR/executive keywords, etc.)
2. **ML Scoring** - LogisticRegression predicts phishing probability, scaled to a 0-100 risk score
3. **Rule-Based Classification** - Score mapped to Safe (<45), Suspicious (45-70), or Phishing (>70)
4. **Escalation Decision** - If borderline (45-70) OR high-impact context AND LLM is enabled, escalate to LLM
5. **LLM Review** (conditional) - Gemini analyzes the email with ML signals as context
6. **Explanation Generation** - Template-based plain-English explanation combining ML signals and optional LLM review

**Q: Why did you choose a two-layer architecture (ML + LLM) instead of using only LLM?**
A: Three reasons:
- **Cost**: LLM calls are expensive. ML handles 70-80% of clear-cut cases without any API cost.
- **Speed**: ML inference is milliseconds vs seconds for LLM calls.
- **Determinism**: ML gives reproducible, consistent results. LLMs can vary across calls. The ML score is the authoritative result and the LLM never overrides it.

**Q: What is the escalation trigger logic?**
A: LLM escalation triggers when BOTH conditions are met:
1. The email is borderline (score 45-70) OR involves high-impact context (finance, HR, or executive keywords detected)
2. LLM is enabled in the configuration

**Q: Why can't the LLM change the ML risk score?**
A: This is a deliberate design constraint (FR-006). The ML score ensures determinism and reproducibility. If the same email is scanned twice, it gets the same score. The LLM provides additional context and reasoning but never modifies the numerical score. This makes the system auditable and trustworthy.

**Q: How is the project structured?**
A: Modular architecture with independent, replaceable components:
- `src/features/extractor.py` - Feature extraction
- `src/scoring/classifier.py` - ML classifier
- `src/decision/rules.py` - Rule-based classification
- `src/escalation/llm_agent.py` - LLM escalation
- `src/explanation/generator.py` - Explanation builder
- `src/pipeline/scanner.py` - Pipeline orchestrator
- `src/evaluation/evaluator.py` - Metrics and evaluation
- `src/models/` - Data models (Signal, ScanResult, LLMReviewResult)
- `src/config.py` - Externalized configuration

Each module can be tested and replaced independently.

---

## 3. ML Model

**Q: Which ML algorithm did you use and why?**
A: Logistic Regression from scikit-learn. Chosen because:
- **Interpretable coefficients** - Each feature gets a weight that explains its contribution
- **Probability output** - `predict_proba()` gives a probability that maps naturally to a 0-100 risk score
- **Lightweight** - Fast training and inference, no GPU required
- **Sufficient for the feature set** - With only 9 hand-crafted features, a simpler model avoids overfitting

**Q: What features does the model use?**
A: 9 features extracted via regex and heuristics:
1. `urgency_keyword_count` - Count of urgent phrases ("urgent", "immediately", "act now", "verify your", etc.)
2. `url_count` - Number of URLs in the email
3. `has_suspicious_url` - Boolean: IP-based URLs or unusual TLDs (.xyz, .tk, etc.)
4. `sender_domain_mismatch` - Boolean: sender domain differs from URL domains in body
5. `financial_keyword_count` - Count of finance terms ("invoice", "payment", "bank account", etc.)
6. `has_attachment_reference` - Boolean: mentions "attached", "see attached", etc.
7. `is_high_impact_context` - Boolean: True if any financial, HR, or executive keywords detected
8. `executive_keyword_count` - Count of executive terms ("ceo", "cfo", "board", "confidential")
9. `hr_keyword_count` - Count of HR terms ("payroll", "salary", "benefits", etc.)

**Q: How does the model produce a risk score?**
A: The LogisticRegression's `predict_proba()` returns the probability of the phishing class (class 1). This probability (0.0 to 1.0) is multiplied by 100 and rounded to produce an integer risk score from 0 to 100.

**Q: How do you explain the model's predictions?**
A: Using the logistic regression coefficients. Each feature has a coefficient (weight) that indicates its contribution to the phishing probability. These are extracted and sorted by absolute value to create Signal objects. The top signals are then converted to plain-English explanations using templates.

**Q: What dataset did you use for training?**
A: The Kaggle Phishing Email Dataset (`naserabdullahalam/phishing-email-dataset`). It contains 82,485 real-world email samples with binary labels (phishing/safe). The dataset includes multiple sources: CEAS_08, Enron, Ling, Nazario, Nigerian Fraud, SpamAssassin.

**Q: How does training work?**
A: The CLI `train` command:
1. Downloads the Kaggle dataset if not present locally (via Kaggle API)
2. Reads the CSV file (columns: `text_combined`, `label`)
3. For each email, runs feature extraction to produce a feature dictionary
4. Trains a scikit-learn Pipeline (DictVectorizer + LogisticRegression)
5. Saves the trained model to disk as a joblib file

**Q: What is the model's performance?**
A: On the evaluation set:
- Recall: 1.000 (100% of phishing emails caught)
- Precision: 1.000
- F1 Score: 1.000

**Q: Why is recall the primary metric?**
A: Because a false negative (missing a phishing email) is far more dangerous than a false positive (flagging a safe email). A missed phishing email can lead to credential theft, financial loss, or data breaches. A false alarm only causes minor inconvenience.

**Q: Could you use a different ML algorithm?**
A: Yes, the modular design allows swapping the classifier. Alternatives could be:
- Random Forest - better with non-linear features
- Gradient Boosting (XGBoost) - higher accuracy potential
- SVM - good for high-dimensional spaces
However, Logistic Regression was chosen specifically for its interpretability, which is a core requirement of this project.

---

## 4. LLM Integration

**Q: How does the LLM integration work?**
A: Using the `openai-agents` framework with Google Gemini:
1. An `AsyncOpenAI` client is created pointing to Google's OpenAI-compatible endpoint
2. An `OpenAIChatCompletionsModel` wraps the Gemini model (gemini-2.5-flash)
3. An `Agent` is created with this model
4. `Runner.run()` executes the agent with a structured prompt containing the email content and ML signals
5. Tracing is disabled via `RunConfig(tracing_disabled=True)` to avoid unnecessary OpenAI trace exports

**Q: Why did you use the openai-agents framework instead of calling Gemini directly?**
A: The openai-agents framework provides:
- A standardized agent abstraction (Agent, Runner pattern)
- Support for multiple LLM providers via the OpenAI-compatible API
- Built-in async support
- Easy model swapping - can change to any OpenAI-compatible provider by changing the base_url and API key

**Q: What prompt do you send to the LLM?**
A: A structured prompt that includes:
- The email content (truncated to 2000 chars)
- The sender address
- The ML classifier's risk score and classification
- The top 5 contributing signals with their values
- Instructions to provide: legitimacy assessment, phishing indicators, agreement/disagreement with ML classification, and recommendations

**Q: What happens if the LLM is unavailable?**
A: The system gracefully falls back to ML-only results. The `_try_escalate()` method catches `LLMUnavailableError` and returns `(False, None)`. The explanation notes "Enhanced review was unavailable; this analysis is based on automated signals only." The user still gets a complete result.

**Q: Why did you use Gemini instead of OpenAI's GPT?**
A: Gemini was chosen as the LLM provider, configured via the `GEMINI_API_KEY` environment variable. The architecture is provider-agnostic - switching to GPT or any other OpenAI-compatible API only requires changing the base_url and API key in the configuration.

---

## 5. Feature Extraction

**Q: Why did you use regex instead of NLP/embeddings for feature extraction?**
A: Several reasons:
- **Speed** - Regex is orders of magnitude faster than transformer-based NLP
- **Interpretability** - Each regex pattern maps to a specific, explainable signal
- **No external dependencies** - Uses Python's stdlib `re` module
- **Determinism** - Same input always produces same features
- **Sufficient for the task** - Phishing emails have well-known textual patterns that regex captures effectively

**Q: How do you detect sender domain mismatch?**
A: Extract the domain from the sender's email address (e.g., "company.com" from "user@company.com"), then check if any URLs in the email body have a different domain. The comparison normalizes for "www." prefixes.

**Q: How do you detect high-impact context?**
A: If any financial keywords (invoice, payment, wire transfer, bank account, tax, billing), HR keywords (benefits, payroll, salary, termination, offer letter), or executive keywords (ceo, cfo, board, confidential) are found in the email, it's flagged as high-impact context.

**Q: What validation do you perform on input?**
A: The `extract_features()` function raises a `ValueError` if the email text is empty or whitespace-only. The sender field can be empty without error.

---

## 6. Configuration & Environment

**Q: How is the project configured?**
A: Via environment variables with the `SCANNER_` prefix and sensible defaults:
- `SCANNER_SAFE_THRESHOLD` (default 45) - Score below this = Safe
- `SCANNER_PHISHING_THRESHOLD` (default 70) - Score above this = Phishing
- `SCANNER_MODEL_PATH` (default "data/model/classifier.joblib")
- `SCANNER_LLM_ENABLED` (default true)
- `SCANNER_LLM_MODEL` (default "gemini-2.5-flash")
- `SCANNER_RANDOM_SEED` (default 42)
- `GEMINI_API_KEY` - Required for LLM escalation

The `ScannerConfig` dataclass is frozen (immutable) and reads env vars on instantiation.

**Q: How do you handle secrets?**
A: API keys are never hardcoded. The `GEMINI_API_KEY` is loaded from environment variables via `python-dotenv`. A `.env.example` file documents required variables without actual values. The `.gitignore` excludes `.env` from version control.

---

## 7. Testing

**Q: How is the project tested?**
A: 50 tests across unit and integration tests:
- **Unit tests** (8 test files): Test each module independently - extractor, classifier, rules, generator, evaluator, LLM agent
- **Integration tests** (2 test files): Test the full pipeline end-to-end with and without LLM
- **Fixtures**: 3 curated example emails (safe, phishing, borderline)

**Q: How do you test the LLM without making actual API calls?**
A: Using `unittest.mock.patch` to mock `agents.run.Runner.run`. The mock returns a controlled `AsyncMock` with a predetermined `final_output`. This isolates the LLM tests from external dependencies and ensures deterministic test results.

**Q: What is your test coverage strategy?**
A: Each module has dedicated tests covering:
- Happy path (expected inputs)
- Edge cases (boundary values like score 44, 45, 70, 71)
- Error paths (empty input, missing API key, LLM unavailable)
- Integration (full pipeline from email text to ScanResult)

**Q: How do you run async tests?**
A: Using `pytest-asyncio` with `asyncio_mode = "auto"` in pyproject.toml. This automatically detects and runs async test functions without needing explicit decorators.

---

## 8. Explanation System

**Q: How are explanations generated?**
A: Template-based approach in `src/explanation/generator.py`:
1. **Verdict** - "This email appears to be safe" / "has characteristics that warrant caution" / "is likely a phishing attempt"
2. **Signal breakdown** - Each significant signal converted to plain English (e.g., "This email uses urgent language 3 times")
3. **LLM review** (if available) - Full LLM analysis appended under "Enhanced Review"
4. **Recommendation** - Actionable next step based on classification

**Q: Why plain English instead of technical output?**
A: The target users are non-technical employees. Terms like "logistic regression coefficient" or "phishing probability 0.88" are meaningless to them. Instead, "This email uses urgent language 3 times, which is common in phishing attempts" is immediately actionable.

---

## 9. Technologies & Dependencies

**Q: What technologies does this project use?**
A:
- **Python 3.13+** - Core language
- **scikit-learn** - ML classifier (LogisticRegression, DictVectorizer, metrics)
- **openai-agents** - LLM agent framework (Agent, Runner, RunConfig)
- **Google Gemini (gemini-2.5-flash)** - LLM provider via OpenAI-compatible API
- **joblib** - Model serialization
- **python-dotenv** - Environment variable management
- **kaggle** - Dataset download
- **pandas** - Data handling
- **pytest + pytest-asyncio** - Testing
- **UV** - Package manager and runner

**Q: Why UV instead of pip?**
A: UV is faster, handles dependency resolution better, and provides a unified workflow with `uv run`, `uv sync`, and `uv pip`. It's the modern Python package manager.

**Q: Why scikit-learn instead of PyTorch/TensorFlow?**
A: The model uses only 9 hand-crafted features. Deep learning frameworks are designed for high-dimensional data (images, text embeddings) and would be massive overkill here. scikit-learn provides exactly what's needed: a simple, fast, interpretable classifier with built-in probability estimation and metrics.

---

## 10. Security & Design Decisions

**Q: How do you prevent the LLM from hallucinating or giving wrong classifications?**
A: The LLM never makes the final decision. The ML score is authoritative and immutable. The LLM only adds supplementary analysis. Even if the LLM says "this is safe" but the ML scores it 90, the classification remains "Phishing". This design prevents LLM hallucinations from affecting the outcome.

**Q: What happens if both ML and LLM disagree?**
A: The ML classification stands. The LLM's disagreement is shown in the explanation as additional context for the user, but the risk score and classification are not changed. Users can see both perspectives and make their own judgment.

**Q: How do you handle large emails?**
A: Email text is truncated to the first 2000 characters before sending to the LLM. This prevents token limit issues and reduces API costs. Feature extraction runs on the full text.

**Q: Is this project production-ready?**
A: It demonstrates production patterns (configuration management, error handling, fallback, testing, modular architecture) but would need additional work for production:
- Model retraining pipeline
- Rate limiting for LLM calls
- Logging and monitoring
- API endpoint (currently CLI-only)
- More sophisticated feature engineering (NLP embeddings, header analysis)
- Larger and more diverse training dataset

---

## 11. Code Quality & Patterns

**Q: What design patterns did you use?**
A:
- **Pipeline pattern** - Sequential processing stages (extract -> score -> classify -> escalate -> explain)
- **Strategy pattern** - Classifier and LLM agent are swappable
- **Fallback pattern** - LLM failure gracefully degrades to ML-only
- **Configuration object** - Frozen dataclass with env var loading
- **Data Transfer Objects** - ScanResult, Signal, LLMReviewResult carry data between layers

**Q: How do you ensure reproducibility?**
A:
- Fixed random seed (default 42) for ML training
- Deterministic feature extraction (regex-based)
- Model serialized with joblib for exact reproduction
- Same input always produces same ML score

**Q: Why is ScannerConfig frozen?**
A: To prevent accidental mutation during pipeline execution. Configuration is set once at startup and remains constant throughout the scanning process. This makes the system more predictable and thread-safe.

---

## 12. Practical Scenarios

**Q: Walk me through what happens when a phishing email is scanned.**
A: Example: "URGENT: Your account is compromised! Click http://fake.com/verify"
1. Feature extraction finds: urgency_keyword_count=2, url_count=1, has_suspicious_url=False, financial_keyword_count=0, is_high_impact_context=False
2. ML classifier produces risk_score=88, with top signals: urgency (weight 0.61), URLs (weight 0.79)
3. Rule engine classifies as "Phishing" (88 > 70), not borderline, but is_high_impact may trigger LLM
4. If LLM triggered: Gemini analyzes and confirms phishing indicators
5. Explanation generated: "This email is likely a phishing attempt. This email uses urgent language 2 times..."
6. ScanResult returned with score=88, classification="Phishing", full explanation

**Q: What happens with a borderline email?**
A: Example: "Dear employee, confirm your payroll details" from hr@company.com
1. Feature extraction: hr_keyword_count=1, is_high_impact_context=True
2. ML scores it 48 (borderline range 45-70)
3. Rule engine: "Suspicious", is_borderline=True, is_high_impact=True
4. Both triggers met -> LLM escalation activated
5. Gemini provides detailed analysis, may agree or disagree with ML
6. Explanation includes both ML signals and LLM review
7. User gets comprehensive analysis to make their own decision

**Q: How would you improve this project?**
A: Potential improvements:
- **Advanced NLP features** - Text embeddings, sentiment analysis, named entity recognition
- **Email header analysis** - SPF/DKIM/DMARC verification, routing analysis
- **Model ensembling** - Combine multiple classifiers for better accuracy
- **Active learning** - Use user feedback to retrain the model
- **Real-time API** - FastAPI/Flask endpoint for email gateway integration
- **Dashboard** - Web UI showing scan history and analytics
- **Multi-language support** - Handle non-English phishing emails
