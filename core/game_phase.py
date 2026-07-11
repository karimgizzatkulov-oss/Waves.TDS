from __future__ import annotations

from dataclasses import dataclass

from core.i18n import t


@dataclass(frozen=True)
class GamePhase:
    id: str
    label: str
    color: str
    tip: str


def compute_game_phase(wave: int, max_wave: int) -> GamePhase:
    early = GamePhase("early", t("phase.early.label"), "#81c784", t("phase.early.tip"))
    mid = GamePhase("mid", t("phase.mid.label"), "#ffb74d", t("phase.mid.tip"))
    late = GamePhase("late", t("phase.late.label"), "#ff8a80", t("phase.late.tip"))

    if max_wave < 1:
        return early

    wave = max(1, min(int(wave), int(max_wave)))
    third = max(1, max_wave // 3)
    two_thirds = max(third + 1, (2 * max_wave) // 3)

    if wave <= third:
        return early
    if wave <= two_thirds:
        return mid
    return late
