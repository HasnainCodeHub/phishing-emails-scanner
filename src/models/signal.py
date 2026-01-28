"""Signal data structure representing a feature-level influence on classification."""

from dataclasses import dataclass


@dataclass
class Signal:
    """A single feature-level influence on the classification.

    Attributes:
        name: Machine-readable signal name (e.g., "urgency_keyword_count").
        display_name: Plain-English label (e.g., "Urgent language").
        value: Extracted feature value.
        weight: Contribution weight toward risk score.
    """

    name: str
    display_name: str
    value: float | int | bool
    weight: float

    def __repr__(self) -> str:
        return f"Signal({self.name}={self.value}, weight={self.weight:.3f})"
