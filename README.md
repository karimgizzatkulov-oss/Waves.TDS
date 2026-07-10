# Waves.TDS

Wave databases for Tower Defense Simulator helper overlays.

## Files

| File | Mode | Waves |
|------|------|-------|
| `data/easy_waves.json` | Easy | 20 |
| `data/casual_waves.json` | Casual | 25 |
| `data/intermediate_waves.json` | Intermediate | 30 |

Each JSON contains enemy lists per wave (no commander dialogue).

## Sources

- Easy / Casual: manual wiki screenshots
- Intermediate: [TDS Fandom — Intermediate Mode/Waves](https://tds.fandom.com/wiki/Intermediate_Mode/Waves) (11 Dec 2024 – Present)

## Format

```json
{
  "meta": { "name": "EASY WAVES", "mode": "easy", "max_wave": 20 },
  "enemy_traits": { "Hidden": ["hidden"], "Armored": ["lead"] },
  "waves": {
    "1": {
      "enemies": [{ "type": "Normal", "count": 4 }]
    }
  }
}
```
