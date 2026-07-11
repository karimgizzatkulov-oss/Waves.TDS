from __future__ import annotations

from core.enemy_stats import EnemyStats
from core.i18n import t
from core.wave_data import EnemyLine


def format_enemy_details(enemy: EnemyLine, enemy_traits: dict[str, list[str]]) -> str:
    lines = [enemy.type, ""]

    lines.append(t("enemy.on_wave", count=enemy.count))
    if enemy.modifiers:
        lines.append(t("enemy.modifiers", mods=", ".join(enemy.modifiers)))

    if enemy.hp is not None:
        lines.append(t("enemy.hp_base", hp=f"{enemy.hp:,}".replace(",", " ")))

    base_traits = list(enemy_traits.get(enemy.type, []))
    if "boss" in base_traits:
        lines.append(t("enemy.class_boss"))

    if enemy.defenses:
        lines.append("")
        lines.append(t("enemy.defenses_title"))
        for defense in enemy.defenses:
            label = EnemyStats.format_defenses((defense,))
            hint = t(f"enemy.hint.{defense}", default="")
            if hint:
                lines.append(f"• {label} — {hint}")
            else:
                lines.append(f"• {label}")
    elif base_traits:
        other = [trait for trait in base_traits if trait != "boss"]
        if other:
            lines.append("")
            lines.append(t("enemy.base_traits", traits=", ".join(other)))
    else:
        lines.append("")
        lines.append(t("enemy.no_defenses"))

    lines.append("")
    lines.append(t("enemy.hp_note"))
    return "\n".join(lines)
