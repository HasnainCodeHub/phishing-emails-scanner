"""Feature extraction from raw email text and sender.

Extracts human-interpretable signals using regex and heuristics.
Per contract scanner-api.md §1.
"""

import re

from src.config import ScannerConfig

# Default config for keyword lists
_DEFAULT_CONFIG = ScannerConfig()

# Urgency patterns
_URGENCY_PATTERNS = [
    r"\burgent\b",
    r"\bimmediately\b",
    r"\bact now\b",
    r"\bexpire[sd]?\b",
    r"\bverify your\b",
    r"\bsuspended\b",
    r"\bwithin \d+ hours?\b",
    r"\bpermanently closed\b",
    r"\brequired immediately\b",
]

# URL pattern
_URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)

# Suspicious URL indicators: IP-based URLs, unusual TLDs
_SUSPICIOUS_TLD_PATTERN = re.compile(
    r"https?://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[^\s/]+\.(?:xyz|top|club|tk|ml|ga|cf|gq|buzz|icu|cam))",
    re.IGNORECASE,
)

_ATTACHMENT_PATTERNS = [
    r"\battached\b",
    r"\battachment\b",
    r"\bsee attached\b",
    r"\bfind attached\b",
    r"\bplease find\b",
]


def _count_keyword_matches(text: str, keywords: tuple[str, ...]) -> int:
    """Count occurrences of keywords (case-insensitive) in text."""
    text_lower = text.lower()
    count = 0
    for keyword in keywords:
        count += len(re.findall(re.escape(keyword), text_lower))
    return count


def _extract_sender_domain(sender: str) -> str | None:
    """Extract domain from sender email address."""
    match = re.search(r"@([\w.-]+)", sender)
    return match.group(1).lower() if match else None


def _check_sender_domain_mismatch(email_text: str, sender: str) -> bool:
    """Check if sender domain differs from domains referenced in email body."""
    sender_domain = _extract_sender_domain(sender)
    if not sender_domain:
        return False

    # Find domains in email body URLs
    body_urls = _URL_PATTERN.findall(email_text)
    for url in body_urls:
        domain_match = re.search(r"https?://([^/:\s]+)", url, re.IGNORECASE)
        if domain_match:
            body_domain = domain_match.group(1).lower()
            # Strip www prefix for comparison
            body_domain = re.sub(r"^www\.", "", body_domain)
            sender_clean = re.sub(r"^www\.", "", sender_domain)
            if body_domain != sender_clean and sender_clean not in body_domain:
                return True
    return False


def extract_features(
    email_text: str,
    sender: str,
    config: ScannerConfig | None = None,
) -> dict[str, float | int | bool]:
    """Extract named features from raw email text and sender.

    Args:
        email_text: Raw email body text (validated non-empty).
        sender: Sender identifier string (may be empty).
        config: Optional scanner config for keyword lists.

    Returns:
        Dictionary mapping feature names to their values.

    Raises:
        ValueError: If email_text is empty or whitespace-only.
    """
    if not email_text or not email_text.strip():
        raise ValueError("email_text must not be empty or whitespace-only")

    if config is None:
        config = _DEFAULT_CONFIG

    text_lower = email_text.lower()

    # Urgency keyword count
    urgency_count = 0
    for pattern in _URGENCY_PATTERNS:
        urgency_count += len(re.findall(pattern, text_lower))

    # URL analysis
    urls = _URL_PATTERN.findall(email_text)
    url_count = len(urls)
    has_suspicious_url = bool(_SUSPICIOUS_TLD_PATTERN.search(email_text))

    # Sender domain mismatch
    sender_domain_mismatch = _check_sender_domain_mismatch(email_text, sender)

    # Financial keyword count
    financial_count = _count_keyword_matches(email_text, config.finance_keywords)

    # Attachment reference
    has_attachment = any(
        re.search(pattern, text_lower) for pattern in _ATTACHMENT_PATTERNS
    )

    # Executive keyword count
    executive_count = _count_keyword_matches(email_text, config.executive_keywords)

    # HR keyword count
    hr_count = _count_keyword_matches(email_text, config.hr_keywords)

    # High-impact context
    is_high_impact = financial_count > 0 or hr_count > 0 or executive_count > 0

    return {
        "urgency_keyword_count": urgency_count,
        "url_count": url_count,
        "has_suspicious_url": has_suspicious_url,
        "sender_domain_mismatch": sender_domain_mismatch,
        "financial_keyword_count": financial_count,
        "has_attachment_reference": has_attachment,
        "is_high_impact_context": is_high_impact,
        "executive_keyword_count": executive_count,
        "hr_keyword_count": hr_count,
    }
