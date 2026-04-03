"""
decision_modes.py — The governance/leadership decision modes of Goberment.

Each mode encapsulates a distinct authority structure and decision logic.
Modes are execution-agnostic: they operate on abstract Option objects and
return a chosen option together with a rationale string.

Available modes
---------------
Imperio            — absolute top-down authority; the first option prevails.
President          — democratic; majority weight wins.
EjecutiveAtencion  — attention-priority; highest urgency tag wins.
Armonico           — consensus; the option with least conflict is selected.
Desicion           — pure choice; delegates to the ChoiceEngine directly.
GrupDirection      — collective intelligence; weighted crowd average.
SelfConfidence     — autonomous; the entity trusts its own prior beliefs.
Atractores         — chaotic attractors; the system settles near an attractor.
"""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class Option:
    """
    A single choice candidate.

    Parameters
    ----------
    label : str
        Short human-readable label.
    weight : float
        Relative desirability / vote-count (default 1.0).
    urgency : float
        Priority tag in [0, 1] used by EjecutiveAtencion (default 0.5).
    conflict : float
        Estimated social conflict cost in [0, 1] used by Armonico (default 0.5).
    metadata : dict
        Arbitrary extra payload.
    """

    def __init__(
        self,
        label: str,
        weight: float = 1.0,
        urgency: float = 0.5,
        conflict: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.label = label
        self.weight = float(weight)
        self.urgency = float(urgency)
        self.conflict = float(conflict)
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return (
            f"Option(label={self.label!r}, weight={self.weight:.2f}, "
            f"urgency={self.urgency:.2f}, conflict={self.conflict:.2f})"
        )


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class DecisionMode(ABC):
    """Abstract base for all governance modes."""

    name: str = "base"

    @abstractmethod
    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        """
        Select one option from *options*.

        Returns
        -------
        chosen : Option
            The selected option.
        rationale : str
            Human-readable explanation of the choice.
        """

    def _require_options(self, options: List[Option]) -> None:
        if not options:
            raise ValueError(f"{self.name}: at least one option is required.")


# ---------------------------------------------------------------------------
# Concrete modes
# ---------------------------------------------------------------------------


class Imperio(DecisionMode):
    """
    Imperial mode — absolute top-down authority.

    The sovereign always chooses the first option (or the option whose weight
    is highest when *sovereign_index* is None).  No deliberation occurs.
    """

    name = "Imperio"

    def __init__(self, sovereign_index: Optional[int] = None) -> None:
        self.sovereign_index = sovereign_index

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)
        if self.sovereign_index is not None:
            idx = self.sovereign_index % len(options)
        else:
            idx = max(range(len(options)), key=lambda i: options[i].weight)
        chosen = options[idx]
        return chosen, (
            f"[{self.name}] Sovereign decree: '{chosen.label}' selected "
            f"(index={idx}, weight={chosen.weight:.2f})."
        )


class President(DecisionMode):
    """
    Presidential / democratic mode.

    Each option's *weight* represents accumulated votes.
    The option with the highest total wins.
    """

    name = "President"

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)
        chosen = max(options, key=lambda o: o.weight)
        total = sum(o.weight for o in options)
        pct = (chosen.weight / total * 100) if total > 0 else 0.0
        return chosen, (
            f"[{self.name}] Democratic vote: '{chosen.label}' wins with "
            f"{chosen.weight:.0f}/{total:.0f} votes ({pct:.1f}%)."
        )


class EjecutiveAtencion(DecisionMode):
    """
    Executive-attention mode.

    Focuses on the option with the highest urgency.  Simulates a leadership
    style that reacts to the most pressing item on the agenda.
    """

    name = "EjecutiveAtencion"

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)
        chosen = max(options, key=lambda o: o.urgency)
        return chosen, (
            f"[{self.name}] Executive focus: '{chosen.label}' demands "
            f"immediate attention (urgency={chosen.urgency:.2f})."
        )


class Armonico(DecisionMode):
    """
    Harmonic / consensus mode.

    Selects the option that minimises social conflict.  The community's
    cohesion is the primary value.
    """

    name = "Armonico"

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)
        chosen = min(options, key=lambda o: o.conflict)
        return chosen, (
            f"[{self.name}] Harmonic consensus: '{chosen.label}' minimises "
            f"conflict (conflict={chosen.conflict:.2f})."
        )


class Desicion(DecisionMode):
    """
    Pure-decision mode.

    Delegates entirely to a ChoiceEngine.  The *context* dict should contain
    a 'choice_mode' key (ChoiceMode value) if a specific engine is required.
    Falls back to a deterministic max-weight selection otherwise.
    """

    name = "Desicion"

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)
        # Lazy import to avoid circular dependency
        from goberment.choice_engine import ChoiceEngine, ChoiceMode

        mode = (context or {}).get("choice_mode", ChoiceMode.DETERMINISTIC)
        engine = ChoiceEngine(mode)
        chosen = engine.choose(options)
        return chosen, (
            f"[{self.name}] Pure decision via {engine.mode.name}: "
            f"'{chosen.label}' selected."
        )


class GrupDirection(DecisionMode):
    """
    Group-direction / collective-intelligence mode.

    Computes a weighted average score for each option using both *weight*
    (representing group confidence) and a composite score, then picks the
    highest scorer.
    """

    name = "GrupDirection"

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)

        def score(o: Option) -> float:
            return o.weight * (1.0 - o.conflict) * (0.5 + 0.5 * o.urgency)

        chosen = max(options, key=score)
        return chosen, (
            f"[{self.name}] Collective intelligence: '{chosen.label}' "
            f"emerges as group direction (score={score(chosen):.3f})."
        )


class SelfConfidence(DecisionMode):
    """
    Self-confidence / autonomous mode.

    The entity relies entirely on its own prior beliefs rather than external
    signals.  *context* may contain a 'belief_key' that maps to a label in
    the options list; otherwise the highest-weight option is used.
    """

    name = "SelfConfidence"

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)
        belief_key: Optional[str] = (context or {}).get("belief_key")
        if belief_key:
            matched = [o for o in options if o.label == belief_key]
            if matched:
                chosen = matched[0]
                return chosen, (
                    f"[{self.name}] Inner conviction: '{chosen.label}' aligns "
                    f"with stored belief '{belief_key}'."
                )
        chosen = max(options, key=lambda o: o.weight)
        return chosen, (
            f"[{self.name}] Autonomous trust: '{chosen.label}' selected "
            f"by internal confidence (weight={chosen.weight:.2f})."
        )


class Atractores(DecisionMode):
    """
    Attractors mode — chaotic-systems decision making.

    Models a dynamical system where the state space contains several basins
    of attraction.  Each option is an attractor; the system's trajectory is
    nudged by a simple logistic-map iteration and settles in the basin closest
    to its current state.

    This models decisions that emerge from complex, self-organising processes
    rather than deliberate reasoning.
    """

    name = "Atractores"

    def __init__(self, r: float = 3.7, iterations: int = 20) -> None:
        """
        Parameters
        ----------
        r : float
            Logistic-map growth parameter (chaotic for r > 3.57).
        iterations : int
            Number of map iterations before reading the final state.
        """
        self.r = r
        self.iterations = iterations

    def decide(
        self,
        options: List[Option],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Option, str]:
        self._require_options(options)
        seed: float = (context or {}).get("seed", random.random())
        x = seed
        for _ in range(self.iterations):
            x = self.r * x * (1.0 - x)

        n = len(options)
        attractor_positions = [i / (n - 1 if n > 1 else 1) for i in range(n)]
        closest_idx = min(
            range(n), key=lambda i: abs(attractor_positions[i] - x)
        )
        chosen = options[closest_idx]
        return chosen, (
            f"[{self.name}] Chaotic attractor (r={self.r}, x_final={x:.4f}): "
            f"system settled near '{chosen.label}' (basin {closest_idx})."
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

DECISION_MODES: Dict[str, type] = {
    "Imperio": Imperio,
    "President": President,
    "EjecutiveAtencion": EjecutiveAtencion,
    "Armonico": Armonico,
    "Desicion": Desicion,
    "GrupDirection": GrupDirection,
    "SelfConfidence": SelfConfidence,
    "Atractores": Atractores,
}
