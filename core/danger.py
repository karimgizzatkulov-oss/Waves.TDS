from __future__ import annotations

from typing import Iterable

from core.i18n import t

DANGER_LABELS = {
    (1, 2): ("danger.light", "#4caf50"),
    (3, 4): ("danger.medium", "#ffeb3b"),
    (5, 6): ("danger.high", "#ff9800"),
    (7, 10): ("danger.very_high", "#f44336"),
}

TRAIT_LABELS = {
    "lead": "Lead",
    "hidden": "Hidden",
    "flying": "Flying",
    "boss": "Boss",
}

MODIFIER_TO_TRAIT = {
    "Hidden": "hidden",
    "Lead": "lead",
    "Flying": "flying",
}


def danger_label(score: int) -> tuple[str, str]:
    clamped = max(1, min(10, score))
    for (low, high), (label_key, color) in DANGER_LABELS.items():
        if low <= clamped <= high:
            return t(label_key), color
    return t("danger.medium"), "#ffeb3b"


def _spawn_traits(entry: dict, enemy_traits: dict[str, list[str]]) -> set[str]:
    enemy_type = str(entry.get("type", ""))
    traits = set(enemy_traits.get(enemy_type, []))

    for modifier in entry.get("modifiers", []):
        modifier_name = str(modifier)
        mapped = MODIFIER_TO_TRAIT.get(modifier_name)
        if mapped:
            traits.add(mapped)
        else:
            modifier_key = modifier_name.lower()
            if modifier_key in TRAIT_LABELS:
                traits.add(modifier_key)

    return traits


def compute_danger(
    enemies: Iterable[dict],
    enemy_traits: dict[str, list[str]],
) -> tuple[int, str]:
    score = 1
    total_count = 0
    boss_count = 0
    trait_hits: dict[str, int] = {"lead": 0, "hidden": 0, "flying": 0}

    for entry in enemies:
        count = int(entry.get("count", 1))
        total_count += count
        traits = _spawn_traits(entry, enemy_traits)

        if "boss" in traits:
            boss_count += count
            score += 2
        for trait in ("hidden", "lead", "flying"):
            if trait in traits:
                trait_hits[trait] += count
                score += 1

    score += min(4, total_count // 8)
    score = max(1, min(10, score))

    parts: list[str] = []
    if total_count:
        parts.append(t("danger.enemies_count", count=total_count))
    if boss_count:
        parts.append(t("danger.boss_count", count=boss_count))
    for trait in ("lead", "hidden", "flying"):
        if trait_hits[trait]:
            parts.append(f"{trait_hits[trait]} {TRAIT_LABELS[trait]}")

    if not parts:
        detail = t("danger.few_enemies")
    else:
        detail = t("danger.counts", parts=", ".join(parts))

    return score, detail
