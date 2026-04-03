"""
choice_engine.py — Low-level choice mechanisms for the Goberment framework.

Three fundamentally different ways to make a choice:

DETERMINISTIC  — Pure 0/1 binary logic; the highest-weight option always wins.
ERROR_BASED    — Probabilistic; each option's weight is treated as a probability
                 mass and a weighted random draw is made.  Errors (suboptimal
                 picks) can and do occur.
FREE_WILL      — Stochastic chaos; every option has an equal chance regardless
                 of weight, urgency, or conflict.  Pure autonomy.

The ChoiceEngine is execution-agnostic: it uses only the Python standard
library (random module) and requires no external dependencies.
"""

from __future__ import annotations

import random
from enum import Enum, auto
from typing import List, Optional, Sequence

from goberment.decision_modes import Option


class ChoiceMode(Enum):
    DETERMINISTIC = auto()
    ERROR_BASED = auto()
    FREE_WILL = auto()


class ChoiceEngine:
    """
    Selects one Option from a list according to the configured ChoiceMode.

    Parameters
    ----------
    mode : ChoiceMode
        The selection mechanism to use.
    seed : int | None
        Optional random seed for reproducibility in ERROR_BASED and FREE_WILL
        modes.  When None, system entropy is used.
    """

    def __init__(
        self,
        mode: ChoiceMode = ChoiceMode.DETERMINISTIC,
        seed: Optional[int] = None,
    ) -> None:
        self.mode = mode
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def choose(self, options: Sequence[Option]) -> Option:
        """
        Return one Option from *options* using the configured mechanism.

        Raises
        ------
        ValueError
            If *options* is empty.
        """
        if not options:
            raise ValueError("ChoiceEngine.choose: options must not be empty.")
        options = list(options)
        if self.mode is ChoiceMode.DETERMINISTIC:
            return self._deterministic(options)
        if self.mode is ChoiceMode.ERROR_BASED:
            return self._error_based(options)
        return self._free_will(options)

    def binary_choice(self, option_a: Option, option_b: Option) -> Option:
        """
        Classic 0-vs-1 binary decision between exactly two options.

        In DETERMINISTIC mode the higher-weight option always wins.
        In ERROR_BASED mode the choice is probabilistic.
        In FREE_WILL mode the choice is a fair coin-flip.
        """
        return self.choose([option_a, option_b])

    # ------------------------------------------------------------------
    # Private mechanics
    # ------------------------------------------------------------------

    def _deterministic(self, options: List[Option]) -> Option:
        """Always returns the option with the highest weight (0 or 1 logic)."""
        return max(options, key=lambda o: o.weight)

    def _error_based(self, options: List[Option]) -> Option:
        """
        Weighted random draw — higher weight means higher probability, but the
        "correct" (highest-weight) option is not guaranteed.

        If all weights are zero or negative, falls back to a uniform draw.
        """
        weights = [max(0.0, o.weight) for o in options]
        total = sum(weights)
        if total == 0.0:
            return self._rng.choice(options)
        r = self._rng.uniform(0.0, total)
        cumulative = 0.0
        for option, w in zip(options, weights):
            cumulative += w
            if r <= cumulative:
                return option
        return options[-1]

    def _free_will(self, options: List[Option]) -> Option:
        """Uniformly random — every option has the same chance."""
        return self._rng.choice(options)
