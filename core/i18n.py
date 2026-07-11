from __future__ import annotations

SUPPORTED_LANGUAGES: tuple[tuple[str, str], ...] = (
    ("ru", "Русский"),
    ("en", "English"),
)

_STRINGS: dict[str, dict[str, str]] = {
    "ru": {
        "overlay.waiting": "Ожидание игры…",
        "overlay.scanning": "Сканирование экрана…",
        "overlay.wave_unrecognized": "Волна не распознана",
        "overlay.enemies": "Враги:",
        "overlay.next_wave": "Следующая волна:",
        "overlay.window_fullscreen": "Окно: весь экран",
        "overlay.window_bound": "Окно: {title}",
        "overlay.window_lost": "Окно: {title} — не найдено",
        "overlay.danger": "Опасность: {text} ({score}/10)",
        "overlay.skip": "Skip: {time}",
        "overlay.skip_wave_time": "  |  Время волны: {time}",
        "overlay.skip_unknown": "Skip: нет данных",
        "overlay.tab.wave": "Wave",
        "overlay.tab.help": "Help",
        "overlay.hint": "Wave / Help | клик по имени врага — info | SETUP | F1 | F8",
        "overlay.next_wave_num": "Волна {wave}:",
        "overlay.detection_needed": "Нужен detection:",
        "overlay.final_wave": "🏁 Финальная волна!",
        "overlay.final_wave_tip": "💡 Совет: если ставил farms — не забудь продать их перед концом волны!",
        "overlay.loading_ocr": "Загрузка OCR…",
        "overlay.afk.unconfigured": "Pump: не настроен — открой SETUP",
        "overlay.afk.off": "Pump: выключен{ratio}",
        "overlay.afk.on_ready": "Pump: готов{ratio}",
        "overlay.afk.on_waiting": "Pump: ждём{ratio}",
        "overlay.afk.on_active": "Pump: активен{ratio}",
        "overlay.afk.pressed": "Pump: нажато {presses}{ratio}",
        "overlay.afk.ratio": " ({percent:.0f}% зелёного)",
        "trait.lead": "Lead Detection",
        "trait.hidden": "Hidden Detection",
        "trait.flying": "Flying Detection",
        "danger.light": "Лёгкая",
        "danger.medium": "Средняя",
        "danger.high": "Опасная",
        "danger.very_high": "Очень опасная",
        "danger.few_enemies": "Мало врагов на волне",
        "danger.counts": "Считается: {parts}",
        "danger.enemies_count": "{count} враг.",
        "danger.boss_count": "{count} босс.",
        "phase.early.label": "Early Game",
        "phase.early.tip": "Ранний этап: экономика, базовые башни, первые detections.",
        "phase.mid.label": "Mid Game",
        "phase.mid.tip": "Середина: усиливай DPS и готовь detection под новые угрозы.",
        "phase.late.label": "Late Game",
        "phase.late.tip": "Поздняя игра: максимальный урон, проверь detections перед финалом.",
        "enemy.on_wave": "На этой волне: {count}",
        "enemy.modifiers": "Модификаторы: {mods}",
        "enemy.hp_base": "HP (база): {hp}",
        "enemy.class_boss": "Класс: Boss",
        "enemy.defenses_title": "Защиты на этом спавне:",
        "enemy.base_traits": "Базовые traits: {traits}",
        "enemy.no_defenses": "Особых защит нет",
        "enemy.hp_note": "HP может меняться от режима и модификаторов.",
        "enemy.hint.lead": "обычный урон не проходит",
        "enemy.hint.hidden": "скрыт от большинства башен",
        "enemy.hint.flying": "летит над путём",
        "enemy.hint.ghost": "нужен особый урон",
        "enemy.hint.armored": "получает меньше урона",
        "setup.title": "Настройка",
        "setup.subtitle": "Всё настраивается здесь — отдельные .bat не нужны.",
        "setup.mode.title": "Режим игры",
        "setup.mode.desc": "Сменить Easy / Hardcore и другие режимы",
        "setup.mode.status": "Текущий режим",
        "setup.ocr.title": "Область волны (OCR)",
        "setup.ocr.desc": "Выдели на экране цифры «Wave X / Y»",
        "setup.ocr.status": "OCR область",
        "setup.window.title": "Окно Roblox",
        "setup.window.desc": "Привязать, сменить или отвязать окно игры",
        "setup.window.status": "Окно",
        "setup.pump.title": "Кнопка Pump (AFK)",
        "setup.pump.desc": "Выдели зелёную/серую кнопку Pump на экране",
        "setup.pump.status": "Pump область",
        "setup.opacity": "Прозрачность оверлея",
        "setup.language": "Язык / Language",
        "setup.not_configured": "Не настроено — нажми кнопку выше",
        "setup.window_bound": "Привязано: {title}",
        "setup.window_unbound": "Весь экран (без привязки)",
        "help.title": "Справка",
        "mode.title": "Выберите сложность",
        "mode.subtitle": "Режим должен совпадать с тем, что выбран в игре.",
        "mode.start": "Старт",
        "mode.cancel": "Отмена",
        "mode.waves": "{count} волн",
    },
    "en": {
        "overlay.waiting": "Waiting for game…",
        "overlay.scanning": "Scanning screen…",
        "overlay.wave_unrecognized": "Wave not recognized",
        "overlay.enemies": "Enemies:",
        "overlay.next_wave": "Next wave:",
        "overlay.window_fullscreen": "Window: full screen",
        "overlay.window_bound": "Window: {title}",
        "overlay.window_lost": "Window: {title} — not found",
        "overlay.danger": "Danger: {text} ({score}/10)",
        "overlay.skip": "Skip: {time}",
        "overlay.skip_wave_time": "  |  Wave time: {time}",
        "overlay.skip_unknown": "Skip: no data",
        "overlay.tab.wave": "Wave",
        "overlay.tab.help": "Help",
        "overlay.hint": "Wave / Help | click enemy name — info | SETUP | F1 | F8",
        "overlay.next_wave_num": "Wave {wave}:",
        "overlay.detection_needed": "Detection needed:",
        "overlay.final_wave": "🏁 Final wave!",
        "overlay.final_wave_tip": "💡 Tip: if you placed farms, sell them before the wave ends!",
        "overlay.loading_ocr": "Loading OCR…",
        "overlay.afk.unconfigured": "Pump: not set — open SETUP",
        "overlay.afk.off": "Pump: off{ratio}",
        "overlay.afk.on_ready": "Pump: ready{ratio}",
        "overlay.afk.on_waiting": "Pump: waiting{ratio}",
        "overlay.afk.on_active": "Pump: active{ratio}",
        "overlay.afk.pressed": "Pump: pressed {presses}{ratio}",
        "overlay.afk.ratio": " ({percent:.0f}% green)",
        "trait.lead": "Lead Detection",
        "trait.hidden": "Hidden Detection",
        "trait.flying": "Flying Detection",
        "danger.light": "Light",
        "danger.medium": "Medium",
        "danger.high": "Dangerous",
        "danger.very_high": "Very dangerous",
        "danger.few_enemies": "Few enemies on this wave",
        "danger.counts": "Counts: {parts}",
        "danger.enemies_count": "{count} enemies",
        "danger.boss_count": "{count} boss",
        "phase.early.label": "Early Game",
        "phase.early.tip": "Early game: economy, basic towers, first detections.",
        "phase.mid.label": "Mid Game",
        "phase.mid.tip": "Mid game: scale DPS and prepare detection for new threats.",
        "phase.late.label": "Late Game",
        "phase.late.tip": "Late game: max damage, check detections before the finale.",
        "enemy.on_wave": "On this wave: {count}",
        "enemy.modifiers": "Modifiers: {mods}",
        "enemy.hp_base": "HP (base): {hp}",
        "enemy.class_boss": "Class: Boss",
        "enemy.defenses_title": "Defenses on this spawn:",
        "enemy.base_traits": "Base traits: {traits}",
        "enemy.no_defenses": "No special defenses",
        "enemy.hp_note": "HP may vary by mode and modifiers.",
        "enemy.hint.lead": "normal damage does not work",
        "enemy.hint.hidden": "hidden from most towers",
        "enemy.hint.flying": "flies above the path",
        "enemy.hint.ghost": "needs special damage",
        "enemy.hint.armored": "takes reduced damage",
        "setup.title": "Setup",
        "setup.subtitle": "Configure everything here — no separate .bat files needed.",
        "setup.mode.title": "Game mode",
        "setup.mode.desc": "Switch Easy / Hardcore and other modes",
        "setup.mode.status": "Current mode",
        "setup.ocr.title": "Wave region (OCR)",
        "setup.ocr.desc": "Select the on-screen area with “Wave X / Y”",
        "setup.ocr.status": "OCR region",
        "setup.window.title": "Roblox window",
        "setup.window.desc": "Bind, change, or unbind the game window",
        "setup.window.status": "Window",
        "setup.pump.title": "Pump button (AFK)",
        "setup.pump.desc": "Select the green/gray Pump button on screen",
        "setup.pump.status": "Pump region",
        "setup.opacity": "Overlay opacity",
        "setup.language": "Language / Язык",
        "setup.not_configured": "Not configured — use the button above",
        "setup.window_bound": "Bound: {title}",
        "setup.window_unbound": "Full screen (unbound)",
        "help.title": "Help",
        "mode.title": "Select difficulty",
        "mode.subtitle": "Must match the mode selected in-game.",
        "mode.start": "Start",
        "mode.cancel": "Cancel",
        "mode.waves": "{count} waves",
    },
}

_HELP_SECTIONS: dict[str, list[tuple[str, str]]] = {
    "ru": [
        (
            "Что делает программа",
            "TDS Wave Helper читает номер волны с экрана Roblox (OCR), "
            "подставляет данные из wiki и показывает врагов, опасность, skip, "
            "предупреждения по detection и фазу игры (Early / Mid / Late).",
        ),
        (
            "Первый запуск",
            "1. Запусти setup.bat (один раз) — создаст .venv и установит зависимости.\n"
            "2. Запусти launch.bat — откроется выбор режима (Easy, Hardcore и т.д.).\n"
            "3. Нажми SETUP в оверлее — привязка окна, OCR, Pump, режим, прозрачность.\n"
            "4. Если волна не читается — в SETUP нажми «Область волны (OCR)».",
        ),
        (
            "Окно Roblox (WIN)",
            "WIN — быстрая смена привязки (то же, что кнопка в SETUP).\n"
            "• С привязкой: OCR и оверлей считают координаты от окна Roblox; "
            "оверлей может следовать за окном.\n"
            "• Без привязки: используются абсолютные координаты экрана из config.json.\n"
            "• Если окно закрыли или свернули — статус покажет «не найдено».",
        ),
        (
            "Калибровка OCR",
            "SETUP → «Область волны (OCR)»:\n"
            "• Выдели область, где в игре написано «Wave X / Y».\n"
            "• Enter — сохранить, Esc — отмена.\n"
            "Область должна быть только цифрами волны, без лишнего UI.",
        ),
        (
            "AFK Pump",
            "Автонажатие E, когда кнопка Pump зелёная.\n"
            "• SETUP → «Кнопка Pump (AFK)» — калибровка области.\n"
            "• Клик AFK: OFF/ON или F8 — включить/выключить.\n"
            "• Roblox должен быть в фокусе — E уходит в активное окно.\n"
            "• Несколько нажатий E подряд, пока кнопка зелёная (burst).",
        ),
        (
            "Фазы игры",
            "Early Game — первая треть волн.\n"
            "Mid Game — средняя треть.\n"
            "Late Game — последняя треть.\n"
            "Считается от max_wave выбранного режима.",
        ),
        (
            "Опасность и detection",
            "Опасность (1–10) — оценка текущей волны по типам врагов и модификаторам.\n"
            "«Следующая волна» показывает врагов и новые угрозы: "
            "Lead / Hidden / Flying detection, если на следующей волне "
            "появляется то, чего не было на текущей.",
        ),
        (
            "Горячие клавиши",
            "F1 — компактный режим (меньше окно, только главное).\n"
            "F8 — вкл/выкл AFK Pump.\n"
            "Колёсико мыши — прокрутка содержимого вкладки.",
        ),
        (
            "Кнопки оверлея",
            "SETUP — настройка (режим, OCR, окно, Pump, прозрачность, язык).\n"
            "END — вернуться к выбору режима при старте.\n"
            "WIN — сменить или снять привязку окна.\n"
            "× — закрыть программу.\n"
            "Перетаскивание — за заголовок; после ручного перетаскивания "
            "оверлей перестаёт следовать за окном.",
        ),
        (
            "config.json",
            "Файл в папке проекта. Основные секции:\n"
            "• mode — режим игры\n"
            "• language — ru или en\n"
            "• ocr_region — область номера волны\n"
            "• afk.pump_region — область кнопки Pump\n"
            "• overlay — позиция, прозрачность, compact\n"
            "• window — hwnd и привязка к Roblox\n"
            "Скриншоты на диск не сохраняются — только координаты.",
        ),
        (
            "Если не работает",
            "• Волна не читается — SETUP → OCR, проверь WIN.\n"
            "• Pump не жмёт E — Roblox в фокусе? SETUP → Pump область.\n"
            "• Ошибка при старте — смотри launch.log в папке проекта.\n"
            "• Нет .venv — запусти setup.bat.",
        ),
    ],
    "en": [
        (
            "What it does",
            "TDS Wave Helper reads the wave number from Roblox (OCR), "
            "loads wiki data, and shows enemies, danger, skip, "
            "detection warnings, and game phase (Early / Mid / Late).",
        ),
        (
            "First launch",
            "1. Run setup.bat once — creates .venv and installs dependencies.\n"
            "2. Run launch.bat — pick a mode (Easy, Hardcore, etc.).\n"
            "3. Open SETUP in the overlay — bind window, OCR, Pump, mode, opacity.\n"
            "4. If the wave is not read — SETUP → Wave region (OCR).",
        ),
        (
            "Roblox window (WIN)",
            "WIN — quick bind change (same as the SETUP button).\n"
            "• Bound: OCR and overlay use window-relative coordinates; "
            "overlay can follow the window.\n"
            "• Unbound: absolute screen coordinates from config.json.\n"
            "• Window closed or minimized — status shows not found.",
        ),
        (
            "OCR calibration",
            "SETUP → Wave region (OCR):\n"
            "• Select the on-screen area with “Wave X / Y”.\n"
            "• Enter — save, Esc — cancel.\n"
            "The region should contain only wave digits, no extra UI.",
        ),
        (
            "AFK Pump",
            "Auto-presses E when Pump is green.\n"
            "• SETUP → Pump button (AFK) — calibrate the region.\n"
            "• Click AFK: OFF/ON or F8 to toggle.\n"
            "• Roblox must be focused — E goes to the active window.\n"
            "• Multiple E presses while the button stays green (burst).",
        ),
        (
            "Game phases",
            "Early Game — first third of waves.\n"
            "Mid Game — middle third.\n"
            "Late Game — last third.\n"
            "Based on max_wave for the selected mode.",
        ),
        (
            "Danger and detection",
            "Danger (1–10) rates the current wave by enemy types and modifiers.\n"
            "Next wave shows enemies and new threats: Lead / Hidden / Flying detection "
            "when something new appears on the next wave.",
        ),
        (
            "Hotkeys",
            "F1 — compact mode (smaller window, essentials only).\n"
            "F8 — toggle AFK Pump.\n"
            "Mouse wheel — scroll tab content.",
        ),
        (
            "Overlay buttons",
            "SETUP — settings (mode, OCR, window, Pump, opacity, language).\n"
            "END — return to mode selection at startup.\n"
            "WIN — change or remove window binding.\n"
            "× — close the app.\n"
            "Drag the header to move; manual drag stops follow-window mode.",
        ),
        (
            "config.json",
            "Project folder file. Main sections:\n"
            "• mode — game mode\n"
            "• language — ru or en\n"
            "• ocr_region — wave number region\n"
            "• afk.pump_region — Pump button region\n"
            "• overlay — position, opacity, compact\n"
            "• window — hwnd and Roblox binding\n"
            "Screenshots are not saved — only coordinates.",
        ),
        (
            "Troubleshooting",
            "• Wave not read — SETUP → OCR, check WIN.\n"
            "• Pump does not press E — is Roblox focused? SETUP → Pump region.\n"
            "• Startup error — see launch.log in the project folder.\n"
            "• No .venv — run setup.bat.",
        ),
    ],
}

_current_language = "ru"


def set_language(language: str) -> None:
    global _current_language
    if language in _STRINGS:
        _current_language = language


def get_language() -> str:
    return _current_language


def t(key: str, default: str | None = None, **kwargs: object) -> str:
    table = _STRINGS.get(_current_language, _STRINGS["ru"])
    fallback = _STRINGS["ru"]
    text = table.get(key)
    if text is None:
        text = fallback.get(key, key if default is None else default)
    if kwargs:
        return str(text).format(**kwargs)
    return str(text)


def help_sections() -> list[tuple[str, str]]:
    return list(_HELP_SECTIONS.get(_current_language, _HELP_SECTIONS["ru"]))
