============================================================
  Explainable Phishing Email Scanner
  ML Classification + Controlled LLM Escalation
============================================================

--- Safe Email ---
From: sarah@company.com
Body: Hi John, please find the quarterly report attached. The numbers look good and th...

  Final Verdict: Safe
  Risk Score: 15%
  
  ML Analysis:
    • Attachment reference detected
    • High urgency phrases detected (0 found)
    • HR-related topics detected (0 found)
    • High-impact context (financial, HR, or executive)
    • Executive-level terminology detected (0 found)
  
  User Guidance:
  No immediate action is needed. This email appears legitimate.


============================================================

--- Phishing Email ---
From: security@bank-alerts.com
Body: URGENT: Your bank account has been compromised! Click here immediately to verify...

  Final Verdict: Phishing
  Risk Score: 88%
  
  ML Analysis:
    • High urgency phrases detected (3 found)
    • High-impact context (financial, HR, or executive)
  
  LLM Review:
  Here's a careful assessment of the flagged email:
  
  ---
  
  1.  **Legitimacy Assessment:**
      This email is **highly suspicious and almost certainly illegitimate.** It exhibits numerous classic phishing characteristics designed to induce panic and immediate action.
  
  2.  **Specific Phishing Indicators:**
      *   **Sender Authenticity:** The "From" address `security@bank-alerts.com` is not a legitimate bank domain. Real banks use their official domain (e.g., `bankname.com`). The use of "bank-alerts" is an attempt to appear credible.
      *   **Urgency and Threat:** Phrases like "URGENT," "compromised," and "locked in 24 hours!" are common social engineering tactics to create a sense of panic and pressure the recipient into acting without thinking.
      *   **Malicious Link:** The embedded URL `http://suspicious-site.com/verify` is clearly not a legitimate bank website. This is the primary vector for credential theft.
      *   **Generic Language:** The email refers generally to "Your bank account" instead of a specific account number or the recipient's name, which legitimate banks typically include for sensitive communications.
      *   **Call to Action (CTA):** "Click here immediately to verify your identity" is a direct instruction to engage with the malicious link under duress.
  
  3.  **Agreement with ML Classification:**
      I **fully agree** with the ML classifier's output. The "Risk Score: 88/100" and "Classification: Phishing" are accurate. The "Urgent language" and "High-impact context" are indeed top contributing signals, perfectly reflecting the social engineering tactics employed.
  
  4.  **Specific Recommendations for the Recipient:**
      *   **DO NOT Click:** Absolutely do not click any links within this email.
      *   **DO NOT Reply:** Do not reply to the sender or provide any personal information.
      *   **Report:** Report the email to your organization's IT/security department, or mark it as spam/phishing in your email client.
      *   **Verify Independently:** If you are concerned about your bank account, contact your bank directly using official contact information (e.g., from their official website, the back of your debit/credit card, or a bank statement) • **never** use contact details provided in a suspicious email.
      *   **Delete:** Delete the email after it has been reported.
  
  User Guidance:
  Do not click any links or provide information.
  Report this email to IT/security.
  Delete the email after reporting.

  [LLM Escalation: Triggered]

============================================================

--- Suspicious / Borderline Email (HR Context) ---
From: hr@company.com
Body: Dear employee, please update your payroll bank account details by clicking the s...

  Final Verdict: Suspicious
  Risk Score: 48%
  
  ML Analysis:
    • HR-related topics detected (1 found)
    • High-impact context (financial, HR, or executive)
  
  LLM Review:
  This email presents several red flags commonly associated with phishing attempts, despite the seemingly legitimate sender address.
  
  ---
  
  1.  **Brief explanation of whether this email appears legitimate or suspicious:**
      This email appears **highly suspicious**. While the "From" address *looks* legitimate, the content exhibits several classic social engineering tactics designed to trick recipients into revealing sensitive information.
  
  2.  **Any specific phishing indicators you notice:**
      *   **Generic Greeting:** "Dear employee" is impersonal. Legitimate HR communications, especially those concerning sensitive personal information like payroll, often use the recipient's specific name.
      *   **High-Stakes Request:** The email asks for an update to "payroll bank account details," which is extremely sensitive financial information. Phishers frequently target such data.
      *   **Call to Action via Link:** The instruction to click a "secure link below" (though the link itself is missing from the provided content) is a common phishing technique. Malicious links can lead to fake login pages designed to harvest credentials or banking details.
      *   **Creating Urgency/Justification:** "This is a routine HR verification process" attempts to legitimize the request and disarm the recipient's suspicion, encouraging immediate compliance without critical thought. This is a form of social engineering.
      *   **Potential for Sender Spoofing:** Even if the `hr@company.com` address looks correct, it's trivial for attackers to spoof sender addresses, making it appear as if the email originated from a trusted source.
  
  3.  **Whether you agree with the ML classification or suggest a different one:**
      I **agree** with the "Suspicious" classification and the risk score of 48/100. The ML correctly identified "HR keywords" and "High-impact context" as contributing signals. However, the ML's analysis might not fully capture the nuance of the social engineering tactics like the generic greeting, the creation of false legitimacy, and the implied link action, which collectively push this email firmly into the "highly suspicious" category. Given the critical nature of the request, it leans very close to "Malicious" due to its potential impact.
  
  4.  **Specific recommendations for the recipient:**
      *   **DO NOT click any links** within the email.
      *   **DO NOT reply** to the email or provide any information.
      *   **Verify Independently:** Contact the HR department directly using an officially published and verified method (e.g., a phone number from the company's internal directory, a known internal HR portal URL, or in-person). *Do not use any contact information provided within the suspicious email itself.*
      *   **Report the Email:** Forward the suspicious email to the company's IT security team or designated phishing inbox for investigation.
      *   **Be Skeptical:** Legitimate HR requests for sensitive information like bank details are typically handled through secure, internal portals, physical forms, or established multi-factor authentication processes, rarely solely via a direct email link.
  
  User Guidance:
  Exercise caution with this email.
  Avoid clicking links or downloading attachments until you verify the sender.
  Report to IT/security if uncertain.

  [LLM Escalation: Triggered]

============================================================

