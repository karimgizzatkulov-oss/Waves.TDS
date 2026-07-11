from __future__ import annotations

import json
from pathlib import Path

from core.config import ROOT

DEFENSE_LABELS = {
    "lead": "Lead",
    "hidden": "Hidden",
    "flying": "Flying",
    "ghost": "Ghost",
    "armored": "Armored",
}

MODIFIER_TO_TRAIT = {
    "Hidden": "hidden",
    "Lead": "lead",
    "Flying": "flying",
    "Ghost": "ghost",
}


class EnemyStats:
    def __init__(self, data_dir: Path | None = None) -> None:
        path = (data_dir or ROOT / "data") / "enemy_stats.json"
        self._stats: dict[str, dict] = {}
        if path.exists():
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            self._stats = payload.get("enemies", {})

    def get(self, enemy_type: str) -> dict:
        return self._stats.get(enemy_type, {})

    def hp(self, enemy_type: str) -> int | None:
        value = self.get(enemy_type).get("hp")
        return int(value) if value is not None else None

    def defenses(self, enemy_type: str) -> tuple[str, ...]:
        raw = self.get(enemy_type).get("defenses", [])
        return tuple(str(item) for item in raw)

    @staticmethod
    def format_defenses(defenses: tuple[str, ...]) -> str:
        if not defenses:
            return ""
        return ", ".join(DEFENSE_LABELS.get(item, item.title()) for item in defenses)
