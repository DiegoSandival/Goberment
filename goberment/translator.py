"""
translator.py — Communication-translation layer for the Goberment framework.

When the "common language" between entities has been destroyed, the Translator
applies one of four strategies to re-establish a channel of communication:

MIMETISMO       — El Mimetismo (Chameleon Effect).
                  The messenger adopts the ideological skin of the target,
                  mirroring its symbols, rhetoric, and values just enough to
                  be heard without being immediately rejected.

EMPATIA_RADICAL — Empatía Radical (Extreme Cognitive Empathy).
                  The messenger temporarily validates the target's worldview —
                  even if it is built on hatred or paranoia — to create a
                  moment of genuine contact.  The self is vacated so the
                  other's perspective can be fully inhabited.

ESPEJO          — Pragmatismo / Diplomacia de Espejo (Mirror Diplomacy).
                  The messenger reflects exactly what the target wants to see
                  in order to reach a larger strategic objective (peace,
                  understanding, survival).  The risk: both sides will call the
                  messenger a traitor.

CODE_SWITCHING  — Alternancia de Códigos (Code-Switching).
                  The messenger changes its entire "operating system" — not
                  just language but behavioural codes, posture, and role —
                  depending on who stands before it.  Tribal chief one moment,
                  silent monk the next.

Usage
-----
    from goberment.translator import Translator, TranslationStrategy

    t = Translator()
    msg = t.translate("We need to stop the war.", strategy=TranslationStrategy.MIMETISMO,
                      source_entity=entity_a, target_entity=entity_b)
    print(msg.adapted_text)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from goberment.entities import Entity


class TranslationStrategy(Enum):
    MIMETISMO = auto()
    EMPATIA_RADICAL = auto()
    ESPEJO = auto()
    CODE_SWITCHING = auto()


@dataclass
class TranslatedMessage:
    """
    The output of a translation operation.

    Attributes
    ----------
    original_text : str
        The raw message before translation.
    adapted_text : str
        The message re-framed according to the strategy.
    strategy : TranslationStrategy
        Strategy that was applied.
    mask : str
        The communicative "mask" worn by the messenger.
    risk_level : float
        Estimated social/political risk of this framing (0 = safe, 1 = lethal).
    metadata : dict
        Arbitrary diagnostics.
    """

    original_text: str
    adapted_text: str
    strategy: TranslationStrategy
    mask: str
    risk_level: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"[{self.strategy.name}] mask={self.mask!r} "
            f"risk={self.risk_level:.2f}\n"
            f"  original : {self.original_text}\n"
            f"  adapted  : {self.adapted_text}"
        )


class Translator:
    """
    Translates messages between entities that no longer share a common language.

    The Translator's core sacrifice: by wearing every mask it becomes, in the
    eyes of each faction, the greatest hypocrite of all.  No-one sees its true
    form because it is always wearing someone else's face.
    """

    # Default mask labels per strategy
    _DEFAULT_MASKS: Dict[TranslationStrategy, str] = {
        TranslationStrategy.MIMETISMO: "chameleon",
        TranslationStrategy.EMPATIA_RADICAL: "empty vessel",
        TranslationStrategy.ESPEJO: "mirror",
        TranslationStrategy.CODE_SWITCHING: "shifter",
    }

    def translate(
        self,
        text: str,
        strategy: TranslationStrategy,
        source_entity: Optional["Entity"] = None,
        target_entity: Optional["Entity"] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TranslatedMessage:
        """
        Translate *text* using the given *strategy*.

        Parameters
        ----------
        text : str
            The message to be translated.
        strategy : TranslationStrategy
            Which communication adaptation to apply.
        source_entity : Entity | None
            The entity sending the message (optional, used for context).
        target_entity : Entity | None
            The entity receiving the message (optional, used for context).
        context : dict | None
            Extra information (e.g. shared beliefs, dialect).

        Returns
        -------
        TranslatedMessage
        """
        ctx = context or {}
        if strategy is TranslationStrategy.MIMETISMO:
            return self._mimetismo(text, source_entity, target_entity, ctx)
        if strategy is TranslationStrategy.EMPATIA_RADICAL:
            return self._empatia_radical(text, source_entity, target_entity, ctx)
        if strategy is TranslationStrategy.ESPEJO:
            return self._espejo(text, source_entity, target_entity, ctx)
        return self._code_switching(text, source_entity, target_entity, ctx)

    # ------------------------------------------------------------------
    # Strategy implementations
    # ------------------------------------------------------------------

    def _mimetismo(
        self,
        text: str,
        source: Optional["Entity"],
        target: Optional["Entity"],
        ctx: Dict[str, Any],
    ) -> TranslatedMessage:
        """
        Adopt the target's ideological skin.

        The message is re-framed using the target's own symbols and vocabulary
        so that it is not perceived as a foreign threat.
        """
        target_dialect = ctx.get("target_dialect", "neutral")
        target_symbol = ctx.get("target_symbol", "our shared values")
        if "target_symbol" not in ctx and target and target.beliefs:
            for _key, _val in target.beliefs.items():
                if isinstance(_val, str):
                    target_symbol = _val
                    break

        adapted = (
            f"[Speaking as one of you — {target_dialect}] "
            f"In the name of {target_symbol}: {text}"
        )
        risk = 0.3 + (0.4 if source and target and source is not target else 0.0)
        return TranslatedMessage(
            original_text=text,
            adapted_text=adapted,
            strategy=TranslationStrategy.MIMETISMO,
            mask=f"chameleon::{target_dialect}",
            risk_level=min(risk, 1.0),
            metadata={"target_symbol": target_symbol},
        )

    def _empatia_radical(
        self,
        text: str,
        source: Optional["Entity"],
        target: Optional["Entity"],
        ctx: Dict[str, Any],
    ) -> TranslatedMessage:
        """
        Vacate the self and fully inhabit the target's worldview.

        Even if that worldview is built on hatred or paranoia, the messenger
        temporarily validates it to create a moment of genuine contact.
        """
        target_fear = ctx.get("target_fear", "the unknown")
        if target and target.beliefs.get("primary_fear"):
            target_fear = target.beliefs["primary_fear"]

        adapted = (
            f"I understand that {target_fear} is a real and present danger to "
            f"you. From inside that reality: {text}"
        )
        return TranslatedMessage(
            original_text=text,
            adapted_text=adapted,
            strategy=TranslationStrategy.EMPATIA_RADICAL,
            mask="empty vessel",
            risk_level=0.5,
            metadata={"validated_fear": target_fear},
        )

    def _espejo(
        self,
        text: str,
        source: Optional["Entity"],
        target: Optional["Entity"],
        ctx: Dict[str, Any],
    ) -> TranslatedMessage:
        """
        Reflect what the target wants to see in order to reach a larger goal.

        The messenger accepts being labelled a traitor by every faction because
        none of them can see the conciliatory intention — only the mask.
        """
        desired_image = ctx.get("desired_image", "a trusted ally")
        if target and target.beliefs.get("desired_ally"):
            desired_image = target.beliefs["desired_ally"]

        adapted = (
            f"[Reflecting: {desired_image}] "
            f"As the partner you have always needed: {text}"
        )
        return TranslatedMessage(
            original_text=text,
            adapted_text=adapted,
            strategy=TranslationStrategy.ESPEJO,
            mask=f"mirror::{desired_image}",
            risk_level=0.7,
            metadata={
                "desired_image": desired_image,
                "traitor_risk": True,
            },
        )

    def _code_switching(
        self,
        text: str,
        source: Optional["Entity"],
        target: Optional["Entity"],
        ctx: Dict[str, Any],
    ) -> TranslatedMessage:
        """
        Switch the entire behavioural operating system for this interaction.

        The messenger is not just changing words; it is changing roles, posture,
        and the implicit rules of the conversation.
        """
        role = ctx.get("role", "neutral mediator")
        os_label = ctx.get("os_label", "default")

        adapted = (
            f"[OS: {os_label} | Role: {role}] {text}"
        )
        return TranslatedMessage(
            original_text=text,
            adapted_text=adapted,
            strategy=TranslationStrategy.CODE_SWITCHING,
            mask=f"switcher::{role}",
            risk_level=0.4,
            metadata={"role": role, "os": os_label},
        )
