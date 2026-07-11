"""Generate data/enemy_stats.json from wiki HP dump and mode enemy_traits."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WIKI_HP = Path(
    r"C:\Users\gnail\.cursor\projects\c-Users-gnail-Projects-starboard-defense-helper"
    r"\agent-tools\d11a0092-8fcf-4430-837c-b0a62d30b325.txt"
)

DEFENSE_LABELS = {
    "lead": "Lead",
    "hidden": "Hidden",
    "flying": "Flying",
    "ghost": "Ghost",
    "armored": "Armored",
}

MANUAL_HP: dict[str, int] = {
    "Armored": 80,
    "Reaver": 120,
    "Elite Lead": 120,
    "Void Pike": 70,
    "Phantom": 35,
    "Elite Phantom": 80,
    "Possessed Armor": 90,
    "Molten Demon": 120,
    "Frost Wraith": 100,
    "Frost Invader": 3000,
    "Deep Freeze": 2000,
    "Trickster Elf": 150,
    "Ghoul": 200,
    "Corrupted Fallen": 250,
    "Fallen Summoner": 400,
    "Elite Soul": 900,
    "Void Floater": 100,
    "Slime": 1200,
    "Hazmat": 100,
    "Breaker2": 50,
    "Breaker3": 80,
    "Breaker4": 120,
    "Enraged": 100,
    "Skeleton": 50,
    "Giant Boss": 2000,
    "Speedy Boss": 1800,
    "Slow Boss": 1600,
    "Necromancer": 250,
    "Grave Digger": 5000,
    "Odd": 15,
    "Swift": 12,
    "Mandrake": 40,
    "Mystery": 10,
    "Voidling": 50,
    "Packed Ice": 250,
    "Frozen": 25,
    "Snowy": 20,
    "Permafrost": 150,
    "Frostmite": 40,
    "Yeti": 800,
}


def parse_wiki_hp(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    hp_map: dict[str, int] = {}
    for line in text.splitlines():
        link_match = re.search(r"\|\[(?:[^\]|]+)\]\([^)]+\)\|([\d,]+)\|", line)
        if link_match:
            name_match = re.search(r"\|\[([^\]]+)\]", line)
            if name_match:
                hp_map[name_match.group(1)] = int(link_match.group(1).replace(",", ""))
            continue
        plain_match = re.search(r"^\|([^|\[\]]+)\|([\d,]+)\|", line.strip())
        if plain_match:
            hp_map[plain_match.group(1).strip()] = int(plain_match.group(2).replace(",", ""))
    return hp_map


def collect_types_and_traits() -> tuple[set[str], dict[str, list[str]]]:
    types: set[str] = set()
    merged_traits: dict[str, set[str]] = {}
    for path in DATA.glob("*_waves.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for enemy_type, traits in data.get("enemy_traits", {}).items():
            types.add(enemy_type)
            merged_traits.setdefault(enemy_type, set()).update(traits)
    return types, {key: sorted(value) for key, value in merged_traits.items()}


def main() -> None:
    wiki_hp = parse_wiki_hp(WIKI_HP)
    types, trait_map = collect_types_and_traits()
    stats: dict[str, dict] = {}

    for enemy_type in sorted(types):
        hp = wiki_hp.get(enemy_type) or MANUAL_HP.get(enemy_type)
        defenses = [trait for trait in trait_map.get(enemy_type, []) if trait in DEFENSE_LABELS]
        entry: dict = {}
        if hp is not None:
            entry["hp"] = hp
        if defenses:
            entry["defenses"] = defenses
        if entry:
            stats[enemy_type] = entry

    output = DATA / "enemy_stats.json"
    payload = {
        "meta": {
            "source": "TDS Wiki + mode enemy_traits",
            "note": "HP может отличаться по режиму и модификаторам",
        },
        "defense_labels": DEFENSE_LABELS,
        "enemies": stats,
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(stats)} entries to {output}")


if __name__ == "__main__":
    main()
