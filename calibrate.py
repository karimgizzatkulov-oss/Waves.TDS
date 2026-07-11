from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.calibrate import run_calibrator


def main() -> None:
    saved = run_calibrator()
    if saved:
        print("OCR region saved to config.json")
    else:
        print("Calibration cancelled")


if __name__ == "__main__":
    main()
