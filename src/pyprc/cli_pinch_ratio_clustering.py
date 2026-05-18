# pinchRatioClustering 控制台脚本入口
# 本模块提供 pinchRatioClustering 控制台脚本的 main 函数。
from __future__ import annotations

import sys

from .core import run_pinch_ratio_clustering_cli


def main() -> int:
    return run_pinch_ratio_clustering_cli(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())

