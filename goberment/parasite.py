"""
parasite.py — Status-quo parasite and resistance dynamics.

The Parasite models dogmatism, tribal hate, and the self-reinforcing loops
that make a system resist all change.  Any new idea is perceived as a threat
that *feeds* and *grows* the parasite.

Key concepts from the problem statement
----------------------------------------
* Sometimiento parasitario (parasitic subjugation): entities trapped in the
  death-circle of hatred develop an immune response that attacks novel ideas,
  making the parasite stronger with each rejected proposal.

* Táctica de la Vacuna (vaccine strategy): to govern the parasite you must
  understand what it feeds on, then weaponise its own mechanics against it —
  redirecting hatred toward a non-lethal target or exhausting it via judo.

* El Peligro del Abismo (abyss danger, Nietzsche): the operator who spends
  too long manipulating the parasite's levers of fear risks forgetting that
  they were ever pretending.  The line between healer and tyrant dissolves.

Usage
-----
    from goberment.parasite import Parasite, ParasiteHost

    host = ParasiteHost(entity=some_entity)
    p = Parasite(virulence=0.6)
    p.infect(host, idea="peace")         # idea rejected, parasite grows
    p.apply_vaccine(host, redirected_to="fictional enemy")
    print(host.entity.parasite_load)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from goberment.entities import Entity


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ResistanceEvent:
    """Record of the parasite rejecting an idea."""

    idea: Any
    load_before: float
    load_after: float
    rationale: str


@dataclass
class ParasiteHost:
    """
    Wraps an Entity to track parasite-specific state.

    Attributes
    ----------
    entity : Entity
        The underlying entity being infected.
    rejection_log : list[ResistanceEvent]
        History of ideas rejected by the parasite.
    abyss_depth : float
        Operator risk metric in [0, 1].  When an interventionist (the healer)
        uses the parasite's own tools for too long, their abyss_depth increases.
        At 1.0 the healer has become the tyrant.
    """

    entity: "Entity"
    rejection_log: List[ResistanceEvent] = field(default_factory=list)
    abyss_depth: float = 0.0


# ---------------------------------------------------------------------------
# Parasite
# ---------------------------------------------------------------------------


class Parasite:
    """
    Models the self-reinforcing ideological parasite.

    Parameters
    ----------
    virulence : float
        How aggressively the parasite grows when a new idea is rejected.
        Range [0, 1].  Default 0.4.
    decay : float
        Natural per-step decay of parasite_load when no ideas are presented.
        Range [0, 1].  Default 0.02.
    """

    def __init__(self, virulence: float = 0.4, decay: float = 0.02) -> None:
        self.virulence = min(1.0, max(0.0, virulence))
        self.decay = min(1.0, max(0.0, decay))

    # ------------------------------------------------------------------
    # Core mechanics
    # ------------------------------------------------------------------

    def infect(
        self,
        host: ParasiteHost,
        idea: Any = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResistanceEvent:
        """
        Present *idea* to the host.  If the host's entity perceives it as a
        threat, the parasite feeds and the load increases.

        Returns a ResistanceEvent describing what happened.
        """
        entity = host.entity
        load_before = entity.parasite_load

        if entity.perceives_as_threat(idea):
            growth = self.virulence * (1.0 - entity.parasite_load)
            entity.parasite_load = min(1.0, entity.parasite_load + growth)
            rationale = (
                f"Idea '{idea}' perceived as threat. "
                f"Parasite grows: {load_before:.2f} → {entity.parasite_load:.2f}."
            )
        else:
            entity.parasite_load = max(0.0, entity.parasite_load - self.decay)
            rationale = (
                f"Idea '{idea}' accepted (or host not sufficiently infected). "
                f"Load: {load_before:.2f} → {entity.parasite_load:.2f}."
            )

        event = ResistanceEvent(
            idea=idea,
            load_before=load_before,
            load_after=entity.parasite_load,
            rationale=rationale,
        )
        host.rejection_log.append(event)
        return event

    def apply_vaccine(
        self,
        host: ParasiteHost,
        redirected_to: str,
        operator: Optional["Entity"] = None,
        abyss_cost: float = 0.1,
    ) -> str:
        """
        The vaccine strategy: redirect the parasite's energy toward a
        non-lethal target instead of attacking the real enemy.

        Side-effect: increases *operator*'s abyss_depth by *abyss_cost* if an
        operator entity is provided — modelling the moral cost of using the
        parasite's own mechanics.

        Returns a narrative description of the intervention.
        """
        entity = host.entity
        load_before = entity.parasite_load
        reduction = self.virulence * 0.5
        entity.parasite_load = max(0.0, entity.parasite_load - reduction)

        narrative = (
            f"[Vaccine] Parasite energy redirected from real targets "
            f"toward '{redirected_to}'. "
            f"Load: {load_before:.2f} → {entity.parasite_load:.2f}."
        )

        if operator is not None:
            host.abyss_depth = min(1.0, host.abyss_depth + abyss_cost)
            if host.abyss_depth >= 0.9:
                narrative += (
                    f" WARNING: Operator '{operator.name}' approaches the abyss "
                    f"(depth={host.abyss_depth:.2f}). "
                    "The line between healer and tyrant is dissolving."
                )
            else:
                narrative += (
                    f" Operator '{operator.name}' moral cost accrued "
                    f"(abyss_depth={host.abyss_depth:.2f})."
                )

        return narrative

    def natural_decay(self, host: ParasiteHost) -> str:
        """
        Apply one step of natural decay to the host's parasite_load.

        Returns a brief status string.
        """
        entity = host.entity
        before = entity.parasite_load
        entity.parasite_load = max(0.0, entity.parasite_load - self.decay)
        return (
            f"Natural decay: {entity.name} load {before:.2f} → "
            f"{entity.parasite_load:.2f}."
        )

    def abyss_warning(self, host: ParasiteHost) -> Optional[str]:
        """
        Return a Nietzsche-style warning if the operator is at risk of
        becoming what they fight.  Returns None when safe.
        """
        if host.abyss_depth >= 0.7:
            return (
                f"'Whoever fights monsters should see to it that in the "
                f"process he does not become a monster.' (Nietzsche) "
                f"Abyss depth: {host.abyss_depth:.2f}."
            )
        return None
