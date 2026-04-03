"""
Goberment — an execution-agnostic decision-making framework.

Models multiple governance/leadership modes, choice mechanisms, communication
translation strategies, and the dynamics of the status-quo parasite.
"""

from goberment.entities import Entity
from goberment.decision_modes import (
    DecisionMode,
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
from goberment.translator import Translator, TranslationStrategy
from goberment.parasite import Parasite, ParasiteHost

__all__ = [
    "Entity",
    "DecisionMode",
    "Imperio",
    "President",
    "EjecutiveAtencion",
    "Armonico",
    "Desicion",
    "GrupDirection",
    "SelfConfidence",
    "Atractores",
    "DECISION_MODES",
    "ChoiceEngine",
    "ChoiceMode",
    "Translator",
    "TranslationStrategy",
    "Parasite",
    "ParasiteHost",
]
