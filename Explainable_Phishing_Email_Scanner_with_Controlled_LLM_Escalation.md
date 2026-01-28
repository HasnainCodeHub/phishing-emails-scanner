# Explainable Phishing Email Scanner with Controlled LLM Escalation

## Objective

Design a phishing email scanner that:

- Assigns a risk score (0–100)
- Classifies emails as Safe / Suspicious / Phishing
- Produces a plain-English explanation suitable for a non-technical user
- Uses an LLM only when necessary

## System Design (Required)

### Functional Requirements

**ML Classifier**

- Any lightweight statistical or ML approach
- Must output:
  - Risk score
  - Top influencing features/signals

**LLM Escalation**

- Triggered only when:
  - Score is borderline (e.g., 45–70), OR
  - Email is high-impact (finance, HR, executives)
- LLM must:
  - Classify the borderline email
  - Summarize reasoning
  - Generate a non-technical explanation
  - Not override the ML score blindly

**Explainability**

- Every decision must answer:
  - What is the verdict?
  - Why?
  - What should the user do?

### Dataset to use

Phishing Email Dataset (Kaggle)

https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset

### Deliverables

- Runnable code/notebook
- README (≤2 pages)
- 3 example email analyses with explanations
- Short reflection:
  - Justify the approach used?
  - Failure modes?
  - Future directions for this approach

### Note:

You are expected to evaluate your solution using appropriate metrics and briefly explain why you chose them. We care more about your reasoning than about achieving the highest score.

### Sample Expected Output

```
Final Verdict: Phishing
Risk Score: 76%

ML Analysis:
• High urgency phrases detected
• External sender with domain mismatch
• Multiple embedded links

LLM Review:
This email pressures the recipient to act quickly and comes from a sender
that does not match the claimed organization.

User Guidance:
Do not click any links or provide information.
Report this email to IT/security.
```
