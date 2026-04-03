"""
entities.py — Base Entity/Agent for the Goberment framework.

An Entity is any actor that can hold a decision mode, communicate via a
Translator, and be subject to (or immune to) Parasite influence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from goberment.decision_modes import DecisionMode
    from goberment.translator import TranslationStrategy


@dataclass
class Entity:
    """
    A generic participant in the Goberment system.

    Attributes
    ----------
    name : str
        Human-readable identifier.
    mode : DecisionMode | None
        The decision mode this entity currently operates under.
    beliefs : dict
        A mutable key-value store of the entity's current worldview / values.
    history : list
        Log of decisions made by this entity.
    parasite_load : float
        0.0 = fully free; 1.0 = completely dominated by the parasite.
    active_mask : TranslationStrategy | None
        The communication mask currently worn (set by the Translator).
    """

    name: str
    mode: Optional[Any] = None
    beliefs: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    parasite_load: float = 0.0
    active_mask: Optional[str] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def record(self, event: Dict[str, Any]) -> None:
        """Append an event to the decision history."""
        self.history.append(event)

    def is_infected(self, threshold: float = 0.5) -> bool:
        """Return True when parasite_load exceeds *threshold*."""
        return self.parasite_load >= threshold

    def perceives_as_threat(self, idea: Any) -> bool:
        """
        When heavily infected an entity's immune system attacks new ideas.
        Returns True if the entity will reject *idea* as a threat.
        """
        if not self.is_infected():
            return False
        novelty = 1.0 - self.beliefs.get("openness", 0.5)
        return (self.parasite_load * novelty) > 0.4

    def adopt_belief(self, key: str, value: Any) -> None:
        """Update or add a belief."""
        self.beliefs[key] = value

    def __repr__(self) -> str:
        mode_name = self.mode.__class__.__name__ if self.mode else "None"
        return (
            f"Entity(name={self.name!r}, mode={mode_name}, "
            f"parasite_load={self.parasite_load:.2f})"
        )
