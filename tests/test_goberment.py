"""
tests/test_goberment.py — Unit tests for the Goberment framework.
"""

from __future__ import annotations

import pytest

from goberment.entities import Entity
from goberment.decision_modes import (
    Option,
    Imperio,
    President,
    EjecutiveAtencion,
    Armonico,
    Desicion,
    GrupDirection,
    SelfConfidence,
    Atractores,
    DECISION_MODES,
)
from goberment.choice_engine import ChoiceEngine, ChoiceMode
from goberment.translator import Translator, TranslationStrategy, TranslatedMessage
from goberment.parasite import Parasite, ParasiteHost


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def three_options() -> list[Option]:
    return [
        Option("A", weight=1.0, urgency=0.2, conflict=0.8),
        Option("B", weight=3.0, urgency=0.8, conflict=0.3),
        Option("C", weight=2.0, urgency=0.5, conflict=0.5),
    ]


# ---------------------------------------------------------------------------
# Entity
# ---------------------------------------------------------------------------

class TestEntity:
    def test_default_state(self) -> None:
        e = Entity("test")
        assert e.name == "test"
        assert e.mode is None
        assert e.parasite_load == 0.0
        assert not e.is_infected()
        assert e.history == []

    def test_infected_threshold(self) -> None:
        e = Entity("t", parasite_load=0.6)
        assert e.is_infected()
        assert not e.is_infected(threshold=0.8)

    def test_perceives_as_threat_when_infected(self) -> None:
        e = Entity("t", beliefs={"openness": 0.0}, parasite_load=0.9)
        assert e.perceives_as_threat("new idea")

    def test_no_threat_when_clean(self) -> None:
        e = Entity("t", beliefs={"openness": 0.5}, parasite_load=0.1)
        assert not e.perceives_as_threat("new idea")

    def test_record(self) -> None:
        e = Entity("t")
        e.record({"type": "decision", "value": "A"})
        assert len(e.history) == 1
        assert e.history[0]["value"] == "A"

    def test_adopt_belief(self) -> None:
        e = Entity("t")
        e.adopt_belief("color", "blue")
        assert e.beliefs["color"] == "blue"


# ---------------------------------------------------------------------------
# Decision modes
# ---------------------------------------------------------------------------

class TestImperio:
    def test_selects_sovereign_index(self) -> None:
        opts = three_options()
        mode = Imperio(sovereign_index=0)
        chosen, _ = mode.decide(opts)
        assert chosen is opts[0]

    def test_default_selects_max_weight(self) -> None:
        opts = three_options()
        mode = Imperio()
        chosen, _ = mode.decide(opts)
        assert chosen is opts[1]  # weight=3.0

    def test_raises_on_empty(self) -> None:
        with pytest.raises(ValueError):
            Imperio().decide([])


class TestPresident:
    def test_selects_max_weight(self) -> None:
        opts = three_options()
        chosen, rationale = President().decide(opts)
        assert chosen is opts[1]
        assert "3.0" in rationale or "3/" in rationale

    def test_rationale_contains_percentage(self) -> None:
        opts = [Option("X", weight=100.0), Option("Y", weight=0.0)]
        _, rationale = President().decide(opts)
        assert "100.0%" in rationale


class TestEjecutiveAtencion:
    def test_selects_max_urgency(self) -> None:
        opts = three_options()
        chosen, _ = EjecutiveAtencion().decide(opts)
        assert chosen is opts[1]  # urgency=0.8


class TestArmonico:
    def test_selects_min_conflict(self) -> None:
        opts = three_options()
        chosen, _ = Armonico().decide(opts)
        assert chosen is opts[1]  # conflict=0.3


class TestDesicion:
    def test_returns_an_option(self) -> None:
        opts = three_options()
        chosen, rationale = Desicion().decide(opts)
        assert chosen in opts
        assert "Desicion" in rationale


class TestGrupDirection:
    def test_returns_an_option(self) -> None:
        opts = three_options()
        chosen, _ = GrupDirection().decide(opts)
        assert chosen in opts


class TestSelfConfidence:
    def test_uses_belief_key(self) -> None:
        opts = three_options()
        chosen, _ = SelfConfidence().decide(opts, context={"belief_key": "C"})
        assert chosen is opts[2]

    def test_falls_back_to_weight(self) -> None:
        opts = three_options()
        chosen, _ = SelfConfidence().decide(opts, context={"belief_key": "Z"})
        assert chosen is opts[1]  # max weight


class TestAtractores:
    def test_returns_an_option(self) -> None:
        opts = three_options()
        chosen, rationale = Atractores(r=3.7, iterations=20).decide(
            opts, context={"seed": 0.4}
        )
        assert chosen in opts
        assert "Atractores" in rationale

    def test_deterministic_with_seed(self) -> None:
        opts = three_options()
        mode = Atractores(r=3.8, iterations=25)
        c1, _ = mode.decide(opts, context={"seed": 0.123})
        c2, _ = mode.decide(opts, context={"seed": 0.123})
        assert c1 is c2


class TestDecisionModesRegistry:
    def test_all_modes_present(self) -> None:
        expected = {
            "Imperio", "President", "EjecutiveAtencion", "Armonico",
            "Desicion", "GrupDirection", "SelfConfidence", "Atractores",
        }
        assert expected == set(DECISION_MODES.keys())


# ---------------------------------------------------------------------------
# Choice engine
# ---------------------------------------------------------------------------

class TestChoiceEngine:
    def test_deterministic_always_max_weight(self) -> None:
        engine = ChoiceEngine(ChoiceMode.DETERMINISTIC)
        a, b = Option("A", weight=10.0), Option("B", weight=1.0)
        for _ in range(20):
            assert engine.binary_choice(a, b).label == "A"

    def test_free_will_uniform_distribution(self) -> None:
        engine = ChoiceEngine(ChoiceMode.FREE_WILL, seed=0)
        a, b = Option("A", weight=100.0), Option("B", weight=1.0)
        results = [engine.binary_choice(a, b).label for _ in range(500)]
        # Both should appear — uniformly, not dominated by weight
        assert "A" in results and "B" in results
        ratio = results.count("A") / 500
        assert 0.3 < ratio < 0.7  # roughly 50/50

    def test_error_based_can_pick_lower_weight(self) -> None:
        engine = ChoiceEngine(ChoiceMode.ERROR_BASED, seed=99)
        low = Option("Low", weight=0.1)
        high = Option("High", weight=0.9)
        results = [engine.binary_choice(low, high).label for _ in range(200)]
        # Lower-weight option must appear at least occasionally
        assert "Low" in results

    def test_empty_options_raises(self) -> None:
        engine = ChoiceEngine(ChoiceMode.DETERMINISTIC)
        with pytest.raises(ValueError):
            engine.choose([])

    def test_zero_weight_fallback(self) -> None:
        engine = ChoiceEngine(ChoiceMode.ERROR_BASED, seed=7)
        opts = [Option("X", weight=0.0), Option("Y", weight=0.0)]
        chosen = engine.choose(opts)
        assert chosen in opts


# ---------------------------------------------------------------------------
# Translator
# ---------------------------------------------------------------------------

class TestTranslator:
    def setup_method(self) -> None:
        self.t = Translator()
        self.source = Entity("Source")
        self.target = Entity(
            "Target",
            beliefs={"primary_fear": "oppression", "desired_ally": "liberator"},
        )

    def _translate(
        self,
        strategy: TranslationStrategy,
        ctx: dict | None = None,
    ) -> TranslatedMessage:
        return self.t.translate(
            "test message",
            strategy=strategy,
            source_entity=self.source,
            target_entity=self.target,
            context=ctx or {},
        )

    def test_mimetismo_contains_dialect(self) -> None:
        msg = self._translate(
            TranslationStrategy.MIMETISMO,
            {"target_dialect": "revolutionary"},
        )
        assert "revolutionary" in msg.adapted_text
        assert msg.strategy is TranslationStrategy.MIMETISMO
        assert 0.0 <= msg.risk_level <= 1.0

    def test_empatia_radical_validates_fear(self) -> None:
        msg = self._translate(TranslationStrategy.EMPATIA_RADICAL)
        assert "oppression" in msg.adapted_text
        assert msg.strategy is TranslationStrategy.EMPATIA_RADICAL

    def test_espejo_reflects_desired_image(self) -> None:
        msg = self._translate(TranslationStrategy.ESPEJO)
        assert "liberator" in msg.adapted_text
        assert msg.metadata.get("traitor_risk") is True

    def test_code_switching_contains_role(self) -> None:
        msg = self._translate(
            TranslationStrategy.CODE_SWITCHING,
            {"role": "monk", "os_label": "silence"},
        )
        assert "monk" in msg.adapted_text
        assert "silence" in msg.adapted_text

    def test_original_text_preserved(self) -> None:
        msg = self._translate(TranslationStrategy.MIMETISMO)
        assert msg.original_text == "test message"

    def test_str_representation(self) -> None:
        msg = self._translate(TranslationStrategy.ESPEJO)
        s = str(msg)
        assert "ESPEJO" in s
        assert "original" in s


# ---------------------------------------------------------------------------
# Parasite
# ---------------------------------------------------------------------------

class TestParasite:
    def setup_method(self) -> None:
        self.entity = Entity(
            "Zealot",
            beliefs={"openness": 0.05},
            parasite_load=0.75,
        )
        self.host = ParasiteHost(entity=self.entity)
        self.parasite = Parasite(virulence=0.5, decay=0.05)

    def test_infect_grows_load_on_threat(self) -> None:
        before = self.entity.parasite_load
        event = self.parasite.infect(self.host, idea="radical change")
        assert event.load_after >= before  # parasite grew or stayed same

    def test_infect_records_event(self) -> None:
        self.parasite.infect(self.host, idea="peace")
        assert len(self.host.rejection_log) == 1

    def test_vaccine_reduces_load(self) -> None:
        before = self.entity.parasite_load
        self.parasite.apply_vaccine(self.host, redirected_to="fictional enemy")
        assert self.entity.parasite_load < before

    def test_vaccine_increases_abyss_depth(self) -> None:
        operator = Entity("Mediator")
        self.parasite.apply_vaccine(
            self.host,
            redirected_to="distraction",
            operator=operator,
            abyss_cost=0.2,
        )
        assert self.host.abyss_depth == pytest.approx(0.2)

    def test_abyss_warning_at_high_depth(self) -> None:
        self.host.abyss_depth = 0.8
        warning = self.parasite.abyss_warning(self.host)
        assert warning is not None
        assert "monster" in warning.lower() or "nietzsche" in warning.lower()

    def test_no_abyss_warning_when_safe(self) -> None:
        self.host.abyss_depth = 0.3
        assert self.parasite.abyss_warning(self.host) is None

    def test_natural_decay_reduces_load(self) -> None:
        before = self.entity.parasite_load
        self.parasite.natural_decay(self.host)
        assert self.entity.parasite_load < before

    def test_load_clamped_at_zero(self) -> None:
        self.entity.parasite_load = 0.01
        for _ in range(50):
            self.parasite.natural_decay(self.host)
        assert self.entity.parasite_load >= 0.0
