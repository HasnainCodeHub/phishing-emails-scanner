import asyncio

from src.config import ScannerConfig
from src.pipeline.scanner import EmailScanner


async def main():
    config = ScannerConfig()
    scanner = EmailScanner(config)

    print("=" * 60)
    print("  Explainable Phishing Email Scanner")
    print("  ML Classification + Controlled LLM Escalation")
    print("=" * 60)
    print()

    test_emails = [
        {
            "label": "Safe Email",
            "text": "Hi John, please find the quarterly report attached. The numbers look good and the team performed well this quarter. Best regards, Sarah",
            "sender": "sarah@company.com",
        },
        {
            "label": "Phishing Email",
            "text": "URGENT: Your bank account has been compromised! Click here immediately to verify your identity: http://suspicious-site.com/verify. Your account will be locked in 24 hours!",
            "sender": "security@bank-alerts.com",
        },
        {
            "label": "Suspicious / Borderline Email (HR Context)",
            "text": "Dear employee, please update your payroll bank account details by clicking the secure link below. This is a routine HR verification process.",
            "sender": "hr@company.com",
        },
    ]

    for email in test_emails:
        print(f"--- {email['label']} ---")
        print(f"From: {email['sender']}")
        print(f"Body: {email['text'][:80]}...")
        print()

        result = await scanner.scan(email["text"], email["sender"])

        for line in result.explanation.split("\n"):
            print(f"  {line}")
        print()
        if result.llm_escalated:
            print(f"  [LLM Escalation: Triggered]")
        print()
        print("=" * 60)
        print()


if __name__ == "__main__":
    asyncio.run(main())
