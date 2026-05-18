# pinchRatioClustering 脚本入口
# 可通过 python pinchRatioClustering.py 直接运行。
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyprc.cli_pinch_ratio_clustering import main


if __name__ == "__main__":
    raise SystemExit(main())

