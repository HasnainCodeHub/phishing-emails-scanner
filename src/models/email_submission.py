"""EmailSubmission data structure for scanner input."""

from dataclasses import dataclass


@dataclass
class EmailSubmission:
    """The input to the scanner pipeline.

    Attributes:
        email_text: Raw email body text. Must not be empty or whitespace-only.
        sender: Sender identifier (email address or name). May be empty.
    """

    email_text: str
    sender: str

    def __post_init__(self) -> None:
        if not self.email_text or not self.email_text.strip():
            raise ValueError("email_text must not be empty or whitespace-only")
