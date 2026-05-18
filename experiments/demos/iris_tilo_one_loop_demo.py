from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
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
from pyprc.structs import TiloPolicyStruct


def _pca_2d(features: np.ndarray) -> np.ndarray:
    centered = features - np.mean(features, axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    return centered @ vt[:2].T


def _fit_to_rect(points_2d: np.ndarray, rect: tuple[int, int, int, int]) -> np.ndarray:
    x0, y0, x1, y1 = rect
    w = max(1, x1 - x0)
    h = max(1, y1 - y0)
    mins = np.min(points_2d, axis=0)
    maxs = np.max(points_2d, axis=0)
    span = np.maximum(maxs - mins, 1e-12)
    norm = (points_2d - mins) / span
    px = x0 + 20 + norm[:, 0] * (w - 40)
    py = y1 - 20 - norm[:, 1] * (h - 40)
    return np.column_stack([px, py])


def _draw_scatter(
    draw: ImageDraw.ImageDraw,
    coords: np.ndarray,
    labels: np.ndarray,
    rect: tuple[int, int, int, int],
    title: str,
    legend: dict[int, str],
    palette: dict[int, tuple[int, int, int]],
) -> None:
    x0, y0, x1, y1 = rect
    draw.rectangle(rect, outline=(0, 0, 0), width=2)
    draw.text((x0 + 8, y0 + 8), title, fill=(0, 0, 0), font=ImageFont.load_default())
    for i, (xv, yv) in enumerate(coords):
        label = int(labels[i])
        color = palette.get(label, (90, 90, 90))
        r = 3
        draw.ellipse((xv - r, yv - r, xv + r, yv + r), fill=color, outline=color)
    legend_y = y0 + 24
    for key, text in legend.items():
        color = palette.get(key, (90, 90, 90))
        draw.rectangle((x1 - 180, legend_y, x1 - 168, legend_y + 12), fill=color, outline=color)
        draw.text((x1 - 162, legend_y), text, fill=(0, 0, 0), font=ImageFont.load_default())
        legend_y += 16


def _draw_boundary(
    draw: ImageDraw.ImageDraw,
    boundary_values: Iterable[float],
    split_loc: int,
    rect: tuple[int, int, int, int],
    title: str,
) -> None:
    values = list(float(v) for v in boundary_values)
    x0, y0, x1, y1 = rect
    draw.rectangle(rect, outline=(0, 0, 0), width=2)
    draw.text((x0 + 8, y0 + 8), title, fill=(0, 0, 0), font=ImageFont.load_default())
    if len(values) < 2:
        return
    vmin = min(values)
    vmax = max(values)
    if abs(vmax - vmin) < 1e-12:
        vmax = vmin + 1.0
    inner_w = max(1, (x1 - x0) - 40)
    inner_h = max(1, (y1 - y0) - 40)
    pts: list[tuple[float, float]] = []
    for i, val in enumerate(values):
        tx = x0 + 20 + (i / (len(values) - 1)) * inner_w
        ty = y1 - 20 - ((val - vmin) / (vmax - vmin)) * inner_h
        pts.append((tx, ty))
    draw.line(pts, fill=(40, 87, 157), width=2)
    split_loc = min(max(split_loc, 0), len(values) - 1)
    sx = pts[split_loc][0]
    draw.line((sx, y0 + 18, sx, y1 - 18), fill=(220, 30, 40), width=2)
    draw.text((sx + 4, y0 + 20), f"split={split_loc}", fill=(220, 30, 40), font=ImageFont.load_default())
    draw.text((x0 + 8, y1 - 16), f"boundary min={vmin:.4f}, max={vmax:.4f}", fill=(0, 0, 0), font=ImageFont.load_default())


def run_demo(data_path: Path, output_dir: Path, seed: int, knn_k: int) -> dict[str, object]:
    data = loadtxt_matrix(data_path)
    true_labels = data[:, 0].astype(int)
    features = data[:, 1:].astype(float)

    adjacency, used_k = knnSimMatrix(features, knn_k, KNNAdjMode.KNN_EITHER_ADJ_GAUSS, sigma=-1.0)
    matrix = MatrixStorage(adjacency)

    _GLOBAL_C_RAND.srand(seed)
    order = initOrder_random(features.shape[0])

    TILO(order, matrix, TiloPolicyStruct())
    root_quality, root_loc, root_metrics = findSplitLocation(adjacency, order, PrcMetricEnum.PinchRatio, True)
    if root_loc < 0:
        raise RuntimeError("TILO 完成后未找到可用切分点，请调整参数后重试。")

    left_order, right_order = order.split(root_loc)
    split_labels = np.full(features.shape[0], -1, dtype=int)
    for idx in left_order.vdata:
        split_labels[idx] = 0
    for idx in right_order.vdata:
        split_labels[idx] = 1

    TILO(left_order, matrix, TiloPolicyStruct())
    left_quality, left_loc, _ = findSplitLocation(adjacency, left_order, PrcMetricEnum.PinchRatio, True)
    TILO(right_order, matrix, TiloPolicyStruct())
    right_quality, right_loc, _ = findSplitLocation(adjacency, right_order, PrcMetricEnum.PinchRatio, True)

    coords = _pca_2d(features)
    canvas = Image.new("RGB", (1380, 980), color=(248, 248, 248))
    draw = ImageDraw.Draw(canvas)

    rect_a = (40, 40, 670, 460)
    rect_b = (710, 40, 1340, 460)
    rect_c = (40, 500, 670, 920)
    rect_d = (710, 500, 1340, 920)

    mapped_a = _fit_to_rect(coords, rect_a)
    mapped_c = _fit_to_rect(coords, rect_c)

    _draw_scatter(
        draw,
        mapped_a,
        true_labels,
        rect_a,
        "Iris (PCA 2D, true labels)",
        legend={0: "setosa", 1: "versicolor", 2: "virginica"},
        palette={0: (31, 119, 180), 1: (44, 160, 44), 2: (214, 39, 40)},
    )
    _draw_boundary(
        draw,
        order.boundary().data(),
        root_loc,
        rect_b,
        "TILO boundary curve + first split",
    )
    _draw_scatter(
        draw,
        mapped_c,
        split_labels,
        rect_c,
        "After first PRC split (one loop)",
        legend={0: "cluster A", 1: "cluster B"},
        palette={0: (255, 127, 14), 1: (148, 103, 189)},
    )

    draw.rectangle(rect_d, outline=(0, 0, 0), width=2)
    draw.text((rect_d[0] + 8, rect_d[1] + 8), "One-loop queue state", fill=(0, 0, 0), font=ImageFont.load_default())
    text_lines = [
        f"seed={seed}, n={features.shape[0]}, knn_k={used_k}",
        f"q0={root_quality:.6f}, t0={root_loc}, |C|={order.size()}",
        f"split -> |C_left|={left_order.size()}, |C_right|={right_order.size()}",
        f"left: q={left_quality:.6f}, t={left_loc}",
        f"right: q={right_quality:.6f}, t={right_loc}",
        "",
        "Pseudo flow:",
        "1) Q <- (q0,t0,C)",
        "2) pop(C), split at t0",
        "3) push(left), push(right)",
        "4) end one loop",
        "",
        f"pinchRatio(root)={root_metrics.pinchRatio:.6f}",
        f"ncut(root)={root_metrics.ncut:.6f}",
    ]
    ty = rect_d[1] + 30
    for line in text_lines:
        draw.text((rect_d[0] + 12, ty), line, fill=(0, 0, 0), font=ImageFont.load_default())
        ty += 18

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / "iris_tilo_prc_one_loop.png"
    canvas.save(image_path)

    summary = {
        "seed": seed,
        "n_samples": int(features.shape[0]),
        "knn_k_used": int(used_k),
        "root": {
            "quality": float(root_quality),
            "split_loc": int(root_loc),
            "left_size": int(left_order.size()),
            "right_size": int(right_order.size()),
            "pinch_ratio": float(root_metrics.pinchRatio),
            "ncut": float(root_metrics.ncut),
        },
        "children": {
            "left": {"quality": float(left_quality), "split_loc": int(left_loc)},
            "right": {"quality": float(right_quality), "split_loc": int(right_loc)},
        },
    }
    summary_path = output_dir / "iris_tilo_prc_one_loop_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "image": str(image_path),
        "summary": str(summary_path),
        "used_k": int(used_k),
        "root_split": int(root_loc),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Iris + TILO/PRC 一次循环切分可视化")
    parser.add_argument("--data", type=Path, default=Path("datasets/iris/iris_all.txt"), help="Iris 数据文件路径")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/demos/iris_tilo_demo"),
        help="输出目录（PNG 与 JSON）",
    )
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--knn-k", type=int, default=-1, help="KNN 邻居数，<=0 表示自动")
    args = parser.parse_args()

    result = run_demo(args.data, args.output_dir, args.seed, args.knn_k)
    print(f"image: {result['image']}")
    print(f"summary: {result['summary']}")
    print(f"used_k: {result['used_k']}, root_split: {result['root_split']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
