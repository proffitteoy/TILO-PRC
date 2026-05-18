from __future__ import annotations

import argparse
import heapq
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyprc.algorithm import TILO, findSplitLocation, initOrder_random
from pyprc.enums import KNNAdjMode, PrcMetricEnum
from pyprc.io import loadtxt_matrix
from pyprc.matrix import MatrixStorage
from pyprc.rng import _GLOBAL_C_RAND
from pyprc.similarity import knnSimMatrix
from pyprc.structs import PrcMetricValues, TiloPolicyStruct


@dataclass
class _ClusterCandidate:
    quality: float
    split_loc: int
    order: object
    metrics: PrcMetricValues


def _json_num(value: float) -> float | None:
    if math.isfinite(value):
        return float(value)
    return None


def _draw_boundary_frame(
    boundary_values: Iterable[float],
    split_loc: int,
    output_path: Path,
    title: str,
    lines: list[str],
) -> None:
    canvas = Image.new("RGB", (1280, 600), color=(248, 248, 248))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    rect = (40, 50, 1240, 450)
    x0, y0, x1, y1 = rect
    draw.rectangle(rect, outline=(0, 0, 0), width=2)
    draw.text((x0 + 8, y0 + 8), title, fill=(0, 0, 0), font=font)

    values = [float(v) for v in boundary_values]
    if len(values) >= 2:
        vmin = min(values)
        vmax = max(values)
        if abs(vmax - vmin) < 1e-12:
            vmax = vmin + 1.0
        inner_w = max(1, (x1 - x0) - 40)
        inner_h = max(1, (y1 - y0) - 50)
        pts: list[tuple[float, float]] = []
        for i, val in enumerate(values):
            tx = x0 + 20 + (i / (len(values) - 1)) * inner_w
            ty = y1 - 20 - ((val - vmin) / (vmax - vmin)) * inner_h
            pts.append((tx, ty))
        draw.line(pts, fill=(40, 87, 157), width=2)
        split_loc = min(max(split_loc, 0), len(values) - 1)
        sx = pts[split_loc][0]
        draw.line((sx, y0 + 20, sx, y1 - 20), fill=(220, 30, 40), width=2)
        draw.text((sx + 4, y0 + 24), f"split={split_loc}", fill=(220, 30, 40), font=font)
        draw.text(
            (x0 + 8, y1 - 14),
            f"boundary min={vmin:.4f}, max={vmax:.4f}",
            fill=(0, 0, 0),
            font=font,
        )

    tx = 52
    ty = 470
    for line in lines:
        draw.text((tx, ty), line, fill=(0, 0, 0), font=font)
        ty += 18

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)


def run_progress(
    data_path: Path,
    output_dir: Path,
    seed: int,
    knn_k: int,
    target_k: int,
) -> dict[str, object]:
    if target_k < 2:
        raise ValueError("--target-k 必须 >= 2，才能看到从二聚类开始的切分过程。")

    data = loadtxt_matrix(data_path)
    features = data[:, 1:]
    adjacency, used_k = knnSimMatrix(features, knn_k, KNNAdjMode.KNN_EITHER_ADJ_GAUSS, sigma=-1.0)
    matrix = MatrixStorage(adjacency)

    _GLOBAL_C_RAND.srand(seed)
    root_order = initOrder_random(features.shape[0])
    TILO(root_order, matrix, TiloPolicyStruct())
    root_quality, root_loc, root_metrics = findSplitLocation(
        adjacency, root_order, PrcMetricEnum.PinchRatio, True
    )

    heap: list[tuple[float, int, _ClusterCandidate]] = []
    counter = 0

    def push_candidate(candidate: _ClusterCandidate) -> None:
        nonlocal counter
        heapq.heappush(heap, (candidate.quality, counter, candidate))
        counter += 1

    push_candidate(
        _ClusterCandidate(
            quality=float(root_quality),
            split_loc=int(root_loc),
            order=root_order,
            metrics=root_metrics,
        )
    )

    loop_index = 0
    history: list[dict[str, object]] = []

    while len(heap) < target_k:
        if not heap:
            break
        before_clusters = len(heap)
        _, _, cur = heapq.heappop(heap)
        if cur.split_loc < 0 or (not math.isfinite(cur.quality)):
            break

        left_order, right_order = cur.order.split(cur.split_loc)
        TILO(left_order, matrix, TiloPolicyStruct())
        left_quality, left_loc, left_metrics = findSplitLocation(
            adjacency, left_order, PrcMetricEnum.PinchRatio, True
        )
        TILO(right_order, matrix, TiloPolicyStruct())
        right_quality, right_loc, right_metrics = findSplitLocation(
            adjacency, right_order, PrcMetricEnum.PinchRatio, True
        )

        push_candidate(
            _ClusterCandidate(
                quality=float(left_quality),
                split_loc=int(left_loc),
                order=left_order,
                metrics=left_metrics,
            )
        )
        push_candidate(
            _ClusterCandidate(
                quality=float(right_quality),
                split_loc=int(right_loc),
                order=right_order,
                metrics=right_metrics,
            )
        )
        after_clusters = len(heap)
        loop_index += 1

        frame_path = output_dir / f"loop_{loop_index:02d}_k{after_clusters}.png"
        _draw_boundary_frame(
            boundary_values=cur.order.boundary().data(),
            split_loc=cur.split_loc,
            output_path=frame_path,
            title=f"TILO boundary + split (loop {loop_index})",
            lines=[
                f"clusters: {before_clusters} -> {after_clusters}",
                f"split cluster size={cur.order.size()}, q={cur.quality:.6f}, t={cur.split_loc}",
                f"left size={left_order.size()}, q={left_quality:.6f}, t={left_loc}",
                f"right size={right_order.size()}, q={right_quality:.6f}, t={right_loc}",
                f"root seed={seed}, knn_k={used_k}, target_k={target_k}",
            ],
        )

        history.append(
            {
                "loop": loop_index,
                "before_clusters": before_clusters,
                "after_clusters": after_clusters,
                "frame": str(frame_path),
                "split_cluster_size": int(cur.order.size()),
                "split_quality": _json_num(cur.quality),
                "split_loc": int(cur.split_loc),
                "left_size": int(left_order.size()),
                "right_size": int(right_order.size()),
                "left_quality": _json_num(left_quality),
                "right_quality": _json_num(right_quality),
                "left_loc": int(left_loc),
                "right_loc": int(right_loc),
            }
        )

    summary = {
        "seed": seed,
        "n_samples": int(features.shape[0]),
        "knn_k_used": int(used_k),
        "target_k": target_k,
        "generated_loops": loop_index,
        "frames": [item["frame"] for item in history],
        "history": history,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "split_progress_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary["summary_path"] = str(summary_path)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Iris 数据集上的 TILO/PRC 多循环切分过程可视化（每循环一张边界图）"
    )
    parser.add_argument("--data", type=Path, default=Path("datasets/iris/iris_all.txt"), help="Iris 数据文件")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/demos/iris_tilo_split_progress"),
        help="输出目录",
    )
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--knn-k", type=int, default=-1, help="KNN 邻居数，<=0 自动")
    parser.add_argument("--target-k", type=int, default=6, help="目标聚类数（>=2）")
    args = parser.parse_args()

    result = run_progress(args.data, args.output_dir, args.seed, args.knn_k, args.target_k)
    print(f"summary: {result['summary_path']}")
    for frame in result["frames"]:
        print(f"frame: {frame}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
