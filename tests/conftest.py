"""Shared test fixtures for the Phishing Email Scanner test suite."""

import pytest

from src.models.signal import Signal


# --- Sample email texts ---

SAFE_EMAIL_TEXT = """Hi John,

Please find attached the quarterly report as discussed in our meeting yesterday.
The numbers look good and the team has been performing well.

Best regards,
Sarah from Accounting
sarah@company.com
"""

SAFE_EMAIL_SENDER = "sarah@company.com"

PHISHING_EMAIL_TEXT = """URGENT: Your account has been suspended!

Dear Customer,

We have detected unauthorized access to your account. You must verify your
identity immediately or your account will be permanently closed within 24 hours.

Click here to verify: http://192.168.1.100/verify-account?id=12345
Update your payment: http://suspicious-domain.xyz/payment

Please provide your bank account details and password to restore access.

Regards,
Security Team
support@bank-secure-verify.com
"""

PHISHING_EMAIL_SENDER = "support@bank-secure-verify.com"

BORDERLINE_EMAIL_TEXT = """Dear Employee,

This is a reminder about the upcoming changes to your benefits enrollment.
Please review the attached document regarding your salary adjustment and
payroll updates for the next quarter.

You may need to update your direct deposit information. Please visit
our HR portal at https://hr-portal.company.com/benefits to review.

Thank you,
HR Department
hr@company.com
"""

BORDERLINE_EMAIL_SENDER = "hr@company.com"


@pytest.fixture
def safe_email_text():
    return SAFE_EMAIL_TEXT


@pytest.fixture
def safe_email_sender():
    return SAFE_EMAIL_SENDER


@pytest.fixture
def phishing_email_text():
    return PHISHING_EMAIL_TEXT


@pytest.fixture
def phishing_email_sender():
    return PHISHING_EMAIL_SENDER


@pytest.fixture
def borderline_email_text():
    return BORDERLINE_EMAIL_TEXT


@pytest.fixture
def borderline_email_sender():
    return BORDERLINE_EMAIL_SENDER


@pytest.fixture
def sample_features_safe():
    return {
        "urgency_keyword_count": 0,
        "url_count": 0,
        "has_suspicious_url": False,
        "sender_domain_mismatch": False,
        "financial_keyword_count": 0,
        "has_attachment_reference": True,
        "is_high_impact_context": False,
        "executive_keyword_count": 0,
        "hr_keyword_count": 0,
    }


@pytest.fixture
def sample_features_phishing():
    return {
        "urgency_keyword_count": 4,
        "url_count": 2,
        "has_suspicious_url": True,
        "sender_domain_mismatch": True,
        "financial_keyword_count": 2,
        "has_attachment_reference": False,
        "is_high_impact_context": True,
        "executive_keyword_count": 0,
        "hr_keyword_count": 0,
    }


@pytest.fixture
def sample_signals():
    return [
        Signal(name="urgency_keyword_count", display_name="Urgent language", value=4, weight=0.85),
        Signal(name="has_suspicious_url", display_name="Suspicious URLs", value=True, weight=0.72),
        Signal(name="sender_domain_mismatch", display_name="Sender domain mismatch", value=True, weight=0.65),
        Signal(name="financial_keyword_count", display_name="Financial keywords", value=2, weight=0.45),
    ]
