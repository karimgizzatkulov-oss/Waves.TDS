from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from core.config import ROOT
from core.danger import MODIFIER_TO_TRAIT, compute_danger, danger_label
from core.enemy_stats import EnemyStats
from core.game_phase import GamePhase, compute_game_phase
from core.i18n import t

MODE_FILES = {
    "easy": "easy_waves.json",
    "casual": "casual_waves.json",
    "intermediate": "intermediate_waves.json",
    "molten": "molten_waves.json",
    "fallen": "fallen_waves.json",
    "frost": "frost_waves.json",
    "hardcore": "hardcore_waves.json",
}

TRAIT_KEYS = ("hidden", "lead", "flying")

DISPLAY_TRAITS = frozenset({"hidden", "lead", "flying", "ghost", "armored"})


def list_mode_options(data_dir: Path | None = None) -> list[dict[str, str | int]]:
    folder = data_dir or (ROOT / "data")
    options: list[dict[str, str | int]] = []

    for mode_id, filename in MODE_FILES.items():
        path = folder / filename
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        meta = data.get("meta", {})
        options.append(
            {
                "id": mode_id,
                "name": str(meta.get("name", mode_id.title())),
                "max_wave": int(meta.get("max_wave", len(data.get("waves", {})))),
            }
        )

    return options


@dataclass(frozen=True)
class EnemyLine:
    type: str
    count: int
    modifiers: tuple[str, ...]
    hp: int | None = None
    defenses: tuple[str, ...] = ()

    def display(self) -> str:
        line = f"{self.count}x {self.type}"
        if self.modifiers:
            line += f" ({', '.join(self.modifiers)})"
        if self.hp is not None:
            line += f" — {self.hp} HP"
        if self.defenses:
            line += f" [{EnemyStats.format_defenses(self.defenses)}]"
        return line


@dataclass(frozen=True)
class WaveInfo:
    wave: int
    max_wave: int
    mode_name: str
    enemies: tuple[EnemyLine, ...]
    danger_score: int
    danger_text: str
    danger_color: str
    danger_detail: str
    skip_at: str | None
    wave_time: str | None
    next_warnings: tuple[str, ...]
    next_wave_enemies: tuple[EnemyLine, ...] = ()
    final_wave_tip: str | None = None
    game_phase: GamePhase | None = None
    enemy_traits: dict[str, list[str]] | None = None


class WaveDatabase:
    def __init__(self, mode: str, data_dir: Path | None = None) -> None:
        self.mode = mode.lower()
        if self.mode not in MODE_FILES:
            supported = ", ".join(sorted(MODE_FILES))
            raise ValueError(f"Unknown mode '{mode}'. Supported: {supported}")

        self.data_dir = data_dir or (ROOT / "data")
        self._data = self._load_mode_file()
        self.meta = self._data.get("meta", {})
        self.enemy_traits: dict[str, list[str]] = self._data.get("enemy_traits", {})
        self.waves: dict[str, dict] = self._data.get("waves", {})
        self.stats = EnemyStats(self.data_dir)

    def _load_mode_file(self) -> dict:
        path = self.data_dir / MODE_FILES[self.mode]
        if not path.exists():
            raise FileNotFoundError(f"Wave data not found: {path}")
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    @property
    def mode_name(self) -> str:
        return str(self.meta.get("name", self.mode.title()))

    @property
    def max_wave(self) -> int:
        return int(self.meta.get("max_wave", len(self.waves)))

    def _spawn_traits(self, item: dict) -> set[str]:
        enemy_type = str(item.get("type", ""))
        traits = set(self.enemy_traits.get(enemy_type, []))

        for modifier in item.get("modifiers", []):
            modifier_name = str(modifier)
            mapped = MODIFIER_TO_TRAIT.get(modifier_name)
            if mapped:
                traits.add(mapped)
            else:
                modifier_key = modifier_name.lower()
                if modifier_key in TRAIT_KEYS:
                    traits.add(modifier_key)

        return traits

    def _spawn_signature(self, item: dict, trait: str) -> str | None:
        if trait not in self._spawn_traits(item):
            return None

        enemy_type = str(item.get("type", ""))
        count = int(item.get("count", 1))
        modifiers = tuple(str(mod) for mod in item.get("modifiers", []))
        line = EnemyLine(
            type=enemy_type,
            count=count,
            modifiers=modifiers,
            hp=self.stats.hp(enemy_type),
            defenses=tuple(sorted(t for t in self._spawn_traits(item) if t in DISPLAY_TRAITS)),
        )
        return line.display()

    def _spawn_trait_key(self, item: dict, trait: str) -> str | None:
        if trait not in self._spawn_traits(item):
            return None

        enemy_type = str(item.get("type", ""))
        base_traits = set(self.enemy_traits.get(enemy_type, []))
        if trait in base_traits:
            return f"type:{enemy_type}|trait:{trait}"

        modifier_traits = sorted(
            str(modifier)
            for modifier in item.get("modifiers", [])
            if MODIFIER_TO_TRAIT.get(str(modifier)) == trait
        )
        if modifier_traits:
            return f"type:{enemy_type}|trait:{trait}|mods:{','.join(modifier_traits)}"

        return f"type:{enemy_type}|trait:{trait}"

    def _build_enemy_line(self, item: dict) -> EnemyLine:
        enemy_type = str(item["type"])
        modifiers = tuple(str(mod) for mod in item.get("modifiers", []))
        spawn_traits = self._spawn_traits(item)
        defenses = tuple(sorted(trait for trait in spawn_traits if trait in DISPLAY_TRAITS))

        return EnemyLine(
            type=enemy_type,
            count=int(item.get("count", 1)),
            modifiers=modifiers,
            hp=self.stats.hp(enemy_type),
            defenses=defenses,
        )

    def _wave_enemies(self, wave: int) -> tuple[EnemyLine, ...]:
        entry = self.waves.get(str(wave))
        if not entry:
            return ()
        return tuple(self._build_enemy_line(item) for item in entry.get("enemies", []))

    def get_wave(self, wave: int) -> WaveInfo | None:
        entry = self.waves.get(str(wave))
        if entry is None:
            return None

        enemies = self._wave_enemies(wave)
        danger_score, danger_detail = compute_danger(entry.get("enemies", []), self.enemy_traits)
        danger_text, danger_color = danger_label(danger_score)

        return WaveInfo(
            wave=wave,
            max_wave=self.max_wave,
            mode_name=self.mode_name,
            enemies=enemies,
            danger_score=danger_score,
            danger_text=danger_text,
            danger_color=danger_color,
            danger_detail=danger_detail,
            skip_at=entry.get("skip_at"),
            wave_time=entry.get("wave_time"),
            next_warnings=tuple(self.get_next_warnings(wave)),
            next_wave_enemies=self._wave_enemies(wave + 1),
            final_wave_tip=t("overlay.final_wave_tip") if wave >= self.max_wave else None,
            game_phase=compute_game_phase(wave, self.max_wave),
            enemy_traits=dict(self.enemy_traits),
        )

    def _wave_trait_spawns(self, wave: int) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, str]] = {trait: {} for trait in TRAIT_KEYS}
        entry = self.waves.get(str(wave))
        if not entry:
            return result

        for item in entry.get("enemies", []):
            for trait in TRAIT_KEYS:
                key = self._spawn_trait_key(item, trait)
                display = self._spawn_signature(item, trait)
                if key and display:
                    result[trait][key] = display
        return result

    def get_next_warnings(self, wave: int) -> list[str]:
        if wave >= self.max_wave:
            return []

        seen: dict[str, set[str]] = {trait: set() for trait in TRAIT_KEYS}
        for past_wave in range(1, wave + 1):
            spawns = self._wave_trait_spawns(past_wave)
            for trait in TRAIT_KEYS:
                seen[trait].update(spawns[trait])

        next_spawns = self._wave_trait_spawns(wave + 1)

        warnings: list[str] = []
        for trait in TRAIT_KEYS:
            new_keys = sorted(set(next_spawns[trait]) - seen[trait])
            if not new_keys:
                continue
            displays = [next_spawns[trait][key] for key in new_keys]
            warnings.append(f"{t(f'trait.{trait}')}:\n  " + "\n  ".join(displays))
        return warnings
