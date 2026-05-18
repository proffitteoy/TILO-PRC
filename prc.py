# 旧版兼容导入入口
# 本文件保留 import prc 的兼容性，实际实现在 pyprc 包中。
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyprc import *  # noqa: F401,F403
