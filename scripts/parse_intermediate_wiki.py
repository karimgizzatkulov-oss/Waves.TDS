import json
import re
from pathlib import Path

WIKI_FILE = Path(
    r"C:\Users\gnail\.cursor\projects\c-Users-gnail-Projects-starboard-defense-helper"
    r"\agent-tools\3dc33e19-5f9e-4186-932d-e74f7ed57c5f.txt"
)
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "intermediate_waves.json"

CHUNK_RE = re.compile(
    r"(\d+)x(?:\*\*)?\[([^\]]+)\]\([^)]+\)(?:\*\*)?"
    r"(?:\((.+)\))?"
)
MOD_NAME_RE = re.compile(r"\[([^\]]+)\]")

MODIFIER_MAP = {
    "Boss": "Boss",
    "Bloated": "Bloated",
    "Nimble": "Nimble",
    "Tank": "Tank",
    "Health Regen": "Health Regen",
    "Hidden": "Hidden",
    "Slime": "Slime",
}


def clean_enemy_name(raw: str) -> str:
    name = raw.split("(")[0].strip()
    name = name.replace("_(Modern_Enemy)", "").replace("_", " ")
    return name


def clean_modifier_name(raw: str) -> str:
    name = raw.split("(")[0].strip()
    return MODIFIER_MAP.get(name, name)


def parse_modifiers(raw: str | None) -> list[str]:
    if not raw:
        return []
    modifiers: list[str] = []
    for part in MOD_NAME_RE.findall(raw):
        cleaned = clean_modifier_name(part)
        if cleaned and cleaned not in modifiers:
            modifiers.append(cleaned)
    return modifiers


def parse_enemy_line(text: str) -> list[dict]:
    enemies: list[dict] = []
    for chunk in text.split(", "):
        match = CHUNK_RE.search(chunk.strip())
        if not match:
            continue
        count, raw_name, raw_mods = match.groups()
        enemy = {"type": clean_enemy_name(raw_name), "count": int(count)}
        modifiers = parse_modifiers(raw_mods)
        if modifiers:
            enemy["modifiers"] = modifiers
        enemies.append(enemy)
    return enemies


def extract_current_waves(lines: list[str]) -> dict[str, str]:
    start = end = None
    for index, line in enumerate(lines):
        if "11 December 2024" in line and "Present" in line:
            start = index
        if start is not None and "25 September 2024" in line:
            end = index
            break

    block = lines[start:end]
    waves: dict[str, str] = {}
    wave_start_re = re.compile(r"^(\d+)\|")

    for line in block:
        line = line.strip()
        match = wave_start_re.match(line)
        if not match:
            continue
        parts = line.split("|")
        enemy_part = next(
            (
                part.strip()
                for part in reversed(parts)
                if re.search(r"\d+x(?:\*\*)?\[", part)
            ),
            "",
        )
        if not enemy_part:
            continue
        waves[match.group(1)] = enemy_part

    return waves


def build_enemy_traits(waves: dict[str, list[dict]]) -> dict[str, list[str]]:
    traits: dict[str, set[str]] = {}
    defaults = {
        "Hidden": {"hidden"},
        "Armored": {"armored"},
        "Reaver": {"armored"},
        "Hidden Boss": {"boss", "hidden"},
        "Speedy Boss": {"boss"},
        "Ghoul": {"boss"},
        "Living Experiment": {"boss"},
        "Failed Experiment": {"boss"},
        "Necromancer": {"boss"},
        "Patient Zero": {"boss"},
    }

    for wave_data in waves.values():
        for enemy in wave_data["enemies"]:
            enemy_type = enemy["type"]
            trait_set = traits.setdefault(enemy_type, set())
            for modifier in enemy.get("modifiers", []):
                if modifier == "Hidden":
                    trait_set.add("hidden")
                if modifier == "Boss":
                    trait_set.add("boss")

    for enemy_type, trait_values in defaults.items():
        trait_set = traits.setdefault(enemy_type, set())
        trait_set.update(trait_values)

    return {name: sorted(values) for name, values in sorted(traits.items())}


def main() -> None:
    lines = WIKI_FILE.read_text(encoding="utf-8").splitlines()
    raw_waves = extract_current_waves(lines)
    parsed_waves = {
        wave: {"enemies": parse_enemy_line(enemy_line)}
        for wave, enemy_line in sorted(raw_waves.items(), key=lambda item: int(item[0]))
    }

    payload = {
        "meta": {
            "name": "INTERMEDIATE",
            "mode": "intermediate",
            "max_wave": 30,
            "source": "https://tds.fandom.com/wiki/Intermediate_Mode/Waves",
            "version": "11 December 2024 – Present",
        },
        "enemy_traits": build_enemy_traits(parsed_waves),
        "waves": parsed_waves,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(parsed_waves)} waves to {OUTPUT}")


if __name__ == "__main__":
    main()
