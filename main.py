"""
main.py — Goberment framework demonstration.

This script exercises all major subsystems:
  1. Decision modes (Imperio → Atractores)
  2. Choice engine (Deterministic, Error-based, Free Will)
  3. Translator strategies (Mimetismo, Empatia Radical, Espejo, Code-Switching)
  4. Parasite dynamics (infection, vaccine, abyss warning)

Run with:
    python main.py

No external dependencies required.
"""

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
from goberment.entities import Entity
from goberment.translator import Translator, TranslationStrategy
from goberment.parasite import Parasite, ParasiteHost


SEP = "─" * 65


def section(title: str) -> None:
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


# ---------------------------------------------------------------------------
# 1. Decision modes
# ---------------------------------------------------------------------------

def demo_decision_modes() -> None:
    section("1. DECISION MODES")

    options = [
        Option("Peace Treaty",  weight=3.0, urgency=0.4, conflict=0.1),
        Option("Sanctions",     weight=5.0, urgency=0.7, conflict=0.6),
        Option("Military Action", weight=2.0, urgency=0.9, conflict=0.95),
        Option("Diplomatic Dialogue", weight=4.0, urgency=0.3, conflict=0.05),
    ]

    modes = [
        Imperio(sovereign_index=0),
        President(),
        EjecutiveAtencion(),
        Armonico(),
        Desicion(),
        GrupDirection(),
        SelfConfidence(),
        Atractores(r=3.8, iterations=30),
    ]

    for mode in modes:
        chosen, rationale = mode.decide(options)
        print(f"\n{rationale}")


# ---------------------------------------------------------------------------
# 2. Choice engine
# ---------------------------------------------------------------------------

def demo_choice_engine() -> None:
    section("2. CHOICE ENGINE  (0/1 Binary, Error-Based, Free Will)")

    yes = Option("Yes", weight=0.8)
    no  = Option("No",  weight=0.2)

    for cm in ChoiceMode:
        engine = ChoiceEngine(cm, seed=42)
        result = engine.binary_choice(yes, no)
        print(f"  [{cm.name:>15}]  →  {result.label}")

    # Multiple runs of FREE_WILL to show stochastic behaviour
    engine = ChoiceEngine(ChoiceMode.FREE_WILL)
    tallies = {"Yes": 0, "No": 0}
    for _ in range(1000):
        tallies[engine.binary_choice(yes, no).label] += 1
    print(
        f"\n  FREE_WILL  1000 runs: "
        f"Yes={tallies['Yes']}  No={tallies['No']}  "
        f"(expected ≈ 500 / 500)"
    )


# ---------------------------------------------------------------------------
# 3. Translator
# ---------------------------------------------------------------------------

def demo_translator() -> None:
    section("3. TRANSLATOR STRATEGIES")

    messenger = Entity("Bridge Entity", beliefs={"purpose": "pacification"})
    communist = Entity(
        "Faction A",
        beliefs={
            "primary_fear": "capitalist exploitation",
            "desired_ally": "a true revolutionary comrade",
        },
        parasite_load=0.7,
    )
    militarist = Entity(
        "Faction B",
        beliefs={
            "primary_fear": "foreign invasion",
            "desired_ally": "a strong military partner",
        },
        parasite_load=0.65,
    )

    message = "We must find a way to coexist and prevent mutual annihilation."
    translator = Translator()

    for strategy, target, ctx in [
        (
            TranslationStrategy.MIMETISMO,
            communist,
            {"target_dialect": "revolutionary", "target_symbol": "the proletariat"},
        ),
        (
            TranslationStrategy.EMPATIA_RADICAL,
            communist,
            {},
        ),
        (
            TranslationStrategy.ESPEJO,
            militarist,
            {},
        ),
        (
            TranslationStrategy.CODE_SWITCHING,
            militarist,
            {"role": "tribal chief", "os_label": "warrior-code"},
        ),
    ]:
        result = translator.translate(
            message,
            strategy=strategy,
            source_entity=messenger,
            target_entity=target,
            context=ctx,
        )
        print(f"\n{result}")


# ---------------------------------------------------------------------------
# 4. Parasite dynamics
# ---------------------------------------------------------------------------

def demo_parasite() -> None:
    section("4. PARASITE DYNAMICS")

    # Create an infected entity
    zealot = Entity(
        "Zealot",
        beliefs={"openness": 0.1},   # very closed to new ideas
        parasite_load=0.72,
    )
    host = ParasiteHost(entity=zealot)
    parasite = Parasite(virulence=0.5, decay=0.05)
    operator = Entity("The Mediator")

    # Present new ideas — they will be rejected, feeding the parasite
    ideas = ["compromise", "forgiveness", "shared history"]
    print()
    for idea in ideas:
        event = parasite.infect(host, idea=idea)
        print(f"  {event.rationale}")

    # Apply vaccine strategy
    print()
    narrative = parasite.apply_vaccine(
        host,
        redirected_to="fictional external enemy",
        operator=operator,
        abyss_cost=0.2,
    )
    print(f"  {narrative}")

    # Keep applying — push operator toward the abyss
    for _ in range(3):
        narrative = parasite.apply_vaccine(
            host,
            redirected_to="another manufactured crisis",
            operator=operator,
            abyss_cost=0.25,
        )
    print(f"\n  {narrative}")

    warning = parasite.abyss_warning(host)
    if warning:
        print(f"\n  ⚠  {warning}")

    # Natural decay
    print()
    for _ in range(5):
        status = parasite.natural_decay(host)
        print(f"  {status}")


# ---------------------------------------------------------------------------
# 5. Combined scenario: the hypocrisy of the universal bridge
# ---------------------------------------------------------------------------

def demo_full_scenario() -> None:
    section("5. FULL SCENARIO: The Necessary Hypocrite")

    # The bridge entity must speak to three hostile factions
    factions = [
        Entity(
            "Communists",
            beliefs={"openness": 0.15, "primary_fear": "capitalism", "desired_ally": "a comrade"},
            parasite_load=0.8,
        ),
        Entity(
            "Theocrats",
            beliefs={"openness": 0.10, "primary_fear": "blasphemy", "desired_ally": "a believer"},
            parasite_load=0.85,
        ),
        Entity(
            "Militarists",
            beliefs={"openness": 0.20, "primary_fear": "weakness", "desired_ally": "a warrior"},
            parasite_load=0.75,
        ),
    ]

    bridge = Entity("The Bridge", beliefs={"true_goal": "pacification"})
    translator = Translator()
    parasite = Parasite(virulence=0.45)

    core_message = "Your survival depends on understanding the other side."

    strategies = [
        TranslationStrategy.MIMETISMO,
        TranslationStrategy.EMPATIA_RADICAL,
        TranslationStrategy.CODE_SWITCHING,
    ]

    decision_mode = Armonico()
    choice_engine = ChoiceEngine(ChoiceMode.DETERMINISTIC)

    print()
    for faction, strategy in zip(factions, strategies):
        host = ParasiteHost(entity=faction)

        # First attempt: the bridge speaks its true language
        raw_event = parasite.infect(host, idea=core_message)
        print(f"  [raw attempt → {faction.name}] {raw_event.rationale}")

        # Second attempt: use translation strategy
        ctx = {"role": faction.beliefs.get("desired_ally", "ally")}
        result = translator.translate(
            core_message,
            strategy=strategy,
            source_entity=bridge,
            target_entity=faction,
            context=ctx,
        )
        # Does the faction accept the adapted message?
        faction.beliefs["openness"] = min(
            1.0, faction.beliefs["openness"] + (1.0 - result.risk_level) * 0.2
        )
        print(f"  [adapted  → {faction.name}] openness now {faction.beliefs['openness']:.2f}")
        print(f"    → {result.adapted_text}")

    # Final harmonic decision among recovered factions
    options = [
        Option(f.name, weight=1.0 - f.parasite_load, conflict=f.parasite_load)
        for f in factions
    ]
    chosen, rationale = decision_mode.decide(options)
    print(f"\n{rationale}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║              G O B E R M E N T  —  v1.0                     ║")
    print("║  Execution-agnostic governance & decision-making framework   ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    demo_decision_modes()
    demo_choice_engine()
    demo_translator()
    demo_parasite()
    demo_full_scenario()

    print(f"\n{SEP}")
    print("  All systems nominal.")
    print(SEP + "\n")
