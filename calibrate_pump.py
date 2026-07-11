from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.calibrate_pump import run_pump_calibrator


def main() -> None:
    saved = run_pump_calibrator()
    if saved:
        print("Pump region saved to config.json")
    else:
        print("Calibration cancelled")


if __name__ == "__main__":
    main()
