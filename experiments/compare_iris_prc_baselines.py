"""Iris 数据集上 PRC 与传统聚类方法对比实验。

设计目标：
1) 固定随机种子，保证可复现；
2) 统一评估指标（ARI / NMI / Purity）；
3) 支持在最小依赖环境下运行（仅 numpy + pyprc 即可跑 PRC/K-Means/DBSCAN）；
4) 若安装了 hdbscan 或 sklearn 的 HDBSCAN，则自动纳入 HDBSCAN 对比。
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pyprc


def load_iris_from_file(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    data = np.loadtxt(path, dtype=float)
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError(f"Invalid iris file format: {path}")
    y_true = data[:, 0].astype(int)
    x = data[:, 1:].astype(float)
    return x, y_true


def standardize_features(x: np.ndarray) -> np.ndarray:
    mu = np.mean(x, axis=0)
    sigma = np.std(x, axis=0)
    sigma = np.where(sigma <= 1e-12, 1.0, sigma)
    return (x - mu) / sigma


def _contingency_table(labels_a: Sequence[int], labels_b: Sequence[int]) -> np.ndarray:
    ua = sorted(set(int(v) for v in labels_a))
    ub = sorted(set(int(v) for v in labels_b))
    ia = {v: i for i, v in enumerate(ua)}
    ib = {v: i for i, v in enumerate(ub)}
    table = np.zeros((len(ua), len(ub)), dtype=np.int64)
    for a, b in zip(labels_a, labels_b):
        table[ia[int(a)], ib[int(b)]] += 1
    return table


def _comb2(x: np.ndarray) -> np.ndarray:
    return x * (x - 1) // 2


def adjusted_rand_index(labels_true: Sequence[int], labels_pred: Sequence[int]) -> float:
    if len(labels_true) != len(labels_pred):
        raise ValueError("labels_true and labels_pred must have the same length")
    n = len(labels_true)
    if n <= 1:
        return 1.0
    table = _contingency_table(labels_true, labels_pred)
    nij = table.astype(np.int64)
    ai = np.sum(nij, axis=1)
    bj = np.sum(nij, axis=0)
    sum_nij = float(np.sum(_comb2(nij)))
    sum_ai = float(np.sum(_comb2(ai)))
    sum_bj = float(np.sum(_comb2(bj)))
    total = float(n * (n - 1) // 2)
    if total <= 0.0:
        return 1.0
    expected = (sum_ai * sum_bj) / total
    max_index = 0.5 * (sum_ai + sum_bj)
    denom = max_index - expected
    if abs(denom) <= 1e-12:
        return 1.0
    return float((sum_nij - expected) / denom)


def normalized_mutual_info(labels_true: Sequence[int], labels_pred: Sequence[int]) -> float:
    if len(labels_true) != len(labels_pred):
        raise ValueError("labels_true and labels_pred must have the same length")
    n = len(labels_true)
    if n == 0:
        return 0.0

    table = _contingency_table(labels_true, labels_pred).astype(float)
    n_float = float(n)
    ai = np.sum(table, axis=1)
    bj = np.sum(table, axis=0)
    ai_nz = ai > 0
    bj_nz = bj > 0
    p_a = ai[ai_nz] / n_float
    p_b = bj[bj_nz] / n_float

    h_a = -float(np.sum(p_a * np.log(p_a))) if p_a.size else 0.0
    h_b = -float(np.sum(p_b * np.log(p_b))) if p_b.size else 0.0

    mi = 0.0
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            nij = table[i, j]
            if nij <= 0:
                continue
            mi += (nij / n_float) * math.log((nij * n_float) / (ai[i] * bj[j]))

    denom = h_a + h_b
    if denom <= 1e-12:
        return 1.0
    return float(2.0 * mi / denom)


def _pairwise_dist2(x: np.ndarray, centers: np.ndarray) -> np.ndarray:
    diff = x[:, None, :] - centers[None, :, :]
    return np.sum(diff * diff, axis=2)


def _kmeans_plus_plus_init(x: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n = x.shape[0]
    centers = np.empty((k, x.shape[1]), dtype=float)
    first = int(rng.integers(0, n))
    centers[0] = x[first]
    min_dist2 = np.sum((x - centers[0]) ** 2, axis=1)
    for c in range(1, k):
        total = float(np.sum(min_dist2))
        if total <= 1e-12:
            idx = int(rng.integers(0, n))
        else:
            probs = min_dist2 / total
            idx = int(rng.choice(n, p=probs))
        centers[c] = x[idx]
        cur_dist2 = np.sum((x - centers[c]) ** 2, axis=1)
        min_dist2 = np.minimum(min_dist2, cur_dist2)
    return centers


def run_kmeans(
    x: np.ndarray,
    n_clusters: int,
    seed: int,
    n_init: int = 20,
    max_iter: int = 300,
    tol: float = 1e-6,
) -> np.ndarray:
    n = x.shape[0]
    best_labels: Optional[np.ndarray] = None
    best_inertia = float("inf")
    base_rng = np.random.default_rng(seed)
    seeds = base_rng.integers(0, 2**31 - 1, size=n_init, endpoint=False)

    for init_seed in seeds:
        rng = np.random.default_rng(int(init_seed))
        centers = _kmeans_plus_plus_init(x, n_clusters, rng)
        labels = np.full(n, -1, dtype=int)
        for _ in range(max_iter):
            dist2 = _pairwise_dist2(x, centers)
            new_labels = np.argmin(dist2, axis=1)
            if np.array_equal(new_labels, labels):
                break
            labels = new_labels

            prev_centers = centers.copy()
            for c in range(n_clusters):
                members = x[labels == c]
                if members.shape[0] == 0:
                    farthest = int(np.argmax(np.min(dist2, axis=1)))
                    centers[c] = x[farthest]
                else:
                    centers[c] = np.mean(members, axis=0)

            shift = float(np.max(np.linalg.norm(centers - prev_centers, axis=1)))
            if shift <= tol:
                break

        final_dist2 = _pairwise_dist2(x, centers)
        inertia = float(np.sum(np.min(final_dist2, axis=1)))
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()

    if best_labels is None:
        raise RuntimeError("K-Means failed to produce labels.")
    return best_labels


def run_dbscan(x: np.ndarray, eps: float, min_samples: int) -> np.ndarray:
    n = x.shape[0]
    dist = np.sqrt(np.sum((x[:, None, :] - x[None, :, :]) ** 2, axis=2))
    neighbors = [np.where(dist[i] <= eps)[0].tolist() for i in range(n)]
    core = np.array([len(nei) >= min_samples for nei in neighbors], dtype=bool)

    labels = np.full(n, -1, dtype=int)
    visited = np.zeros(n, dtype=bool)
    cluster_id = 0

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        if not core[i]:
            continue

        labels[i] = cluster_id
        queue = [i]
        while queue:
            p = queue.pop()
            for q in neighbors[p]:
                if not visited[q]:
                    visited[q] = True
                    if core[q]:
                        queue.append(q)
                if labels[q] == -1:
                    labels[q] = cluster_id
        cluster_id += 1

    return labels


def run_prc(
    data_file: Path,
    num_partitions: int,
    seed: int,
    num_init_orderings: int,
    metric: pyprc.PrcMetricEnum,
    prc_similarity: str = "gauss",
    prc_use_sparse: bool = True,
) -> np.ndarray:
    run_config = pyprc.RunConfigStruct(seed=seed, verboseLevel=0, numberOfPartitions=num_partitions)
    if prc_similarity == "knn":
        sim_type = pyprc.PointSimilarityEnum.KNN_ADJ_SIM
    elif prc_similarity == "gauss":
        sim_type = pyprc.PointSimilarityEnum.GAUSS_ADJ_SIM
    else:
        raise ValueError(f"unknown PRC similarity: {prc_similarity}")
    data_config = pyprc.DataConfigStruct(
        inputFileName=str(data_file),
        fileType=pyprc.FileStructureEnum.POINT_DATA,
        useSparseMatrix=prc_use_sparse,
        pointDataConfig=pyprc.PointDataConfigStruct(
            tagLoc=pyprc.TagModeEnum.FRONT_TAGS,
            simType=sim_type,
        ),
    )
    knn_policy = pyprc.KnnAdjPolicyStruct(
        mode=pyprc.KNNAdjMode.KNN_EITHER_ADJ_GAUSS,
        k=-1,
        sigma=-1.0,
    )
    gauss_policy = pyprc.GaussAdjPolicyStruct()
    policy = pyprc.PrcPolicyStruct(metric=metric)

    matrix_like, _, _ = pyprc.readData(knn_policy, gauss_policy, run_config, data_config)
    matrix = pyprc.MatrixStorage(matrix_like)
    pyprc._GLOBAL_C_RAND.srand(seed)

    best_labels: Optional[np.ndarray] = None
    best_counts: Optional[pyprc.PrcReturnStruct] = None
    best_boundary: List[float] = []

    for run_id in range(num_init_orderings):
        order = pyprc.initOrder_random(matrix.rows())
        counts, labels = pyprc.pinchRatioClustering_storage(matrix, order, num_partitions, policy)
        boundary = sorted(order.boundary().data(), reverse=True)
        if run_id == 0:
            best_counts = counts
            best_labels = labels.copy()
            best_boundary = list(boundary)
            continue
        if pyprc.cless(counts, best_counts, boundary, best_boundary):  # type: ignore[arg-type]
            best_counts = counts
            best_labels = labels.copy()
            best_boundary = list(boundary)

    if best_labels is None:
        raise RuntimeError("PRC failed to produce labels.")
    return best_labels


def run_hdbscan_if_available(
    x: np.ndarray,
    min_cluster_size: int,
    min_samples: int,
) -> Tuple[Optional[np.ndarray], str]:
    try:
        from sklearn.cluster import HDBSCAN as SklearnHDBSCAN  # type: ignore

        model = SklearnHDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples)
        labels = model.fit_predict(x)
        return labels.astype(int), "ok(sklearn.cluster.HDBSCAN)"
    except Exception:
        pass

    try:
        import hdbscan  # type: ignore

        model = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples)
        labels = model.fit_predict(x)
        return labels.astype(int), "ok(hdbscan)"
    except Exception as exc:
        return None, f"skipped({exc.__class__.__name__})"


def summarize_result(
    method: str,
    labels_pred: Optional[np.ndarray],
    labels_true: np.ndarray,
    extra_status: str = "ok",
) -> Dict[str, object]:
    if labels_pred is None:
        return {
            "method": method,
            "status": extra_status,
            "ari": None,
            "nmi": None,
            "purity": None,
            "clusters": None,
            "noise_ratio": None,
        }

    pred = labels_pred.astype(int)
    true = labels_true.astype(int)
    ari = adjusted_rand_index(true.tolist(), pred.tolist())
    nmi = normalized_mutual_info(true.tolist(), pred.tolist())
    purity = pyprc.calcPurity(pred.tolist(), true.tolist())
    unique = set(int(v) for v in pred.tolist())
    n_clusters = len(unique - {-1})
    noise_ratio = float(np.mean(pred == -1))
    return {
        "method": method,
        "status": extra_status,
        "ari": round(float(ari), 6),
        "nmi": round(float(nmi), 6),
        "purity": round(float(purity), 6),
        "clusters": int(n_clusters),
        "noise_ratio": round(noise_ratio, 6),
    }


def save_csv(rows: Sequence[Dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["method", "status", "ari", "nmi", "purity", "clusters", "noise_ratio"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def save_json(payload: Dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _plot_ari_with_matplotlib(rows: Sequence[Dict[str, object]], out_path: Path) -> bool:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        return False

    ok_rows = [r for r in rows if isinstance(r.get("ari"), (int, float))]
    if not ok_rows:
        return False

    methods = [str(r["method"]) for r in ok_rows]
    aris = [float(r["ari"]) for r in ok_rows]
    x = np.arange(len(methods))
    colors = ["#f4a261", "#2a9d8f", "#457b9d", "#e76f51", "#6d597a"][: len(methods)]

    plt.figure(figsize=(10, 5.5), dpi=140)
    bars = plt.bar(x, aris, color=colors, edgecolor="black")
    plt.ylim(0.0, 1.0)
    plt.ylabel("Adjusted Rand Index")
    plt.title("Iris: PRC vs K-Means / DBSCAN / HDBSCAN")
    plt.xticks(x, methods, rotation=15)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars, aris):
        plt.text(bar.get_x() + bar.get_width() / 2.0, val + 0.01, f"{val:.3f}", ha="center", fontsize=9)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    return True


def _plot_ari_with_pil(rows: Sequence[Dict[str, object]], out_path: Path) -> bool:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return False

    ok_rows = [r for r in rows if isinstance(r.get("ari"), (int, float))]
    if not ok_rows:
        return False

    width, height = 1100, 640
    margin_left = 230
    margin_right = 80
    margin_top = 90
    margin_bottom = 70
    bar_gap = 18
    row_height = 46
    bar_h = 26
    axis_w = width - margin_left - margin_right

    img = Image.new("RGB", (width, height), color=(245, 246, 248))
    draw = ImageDraw.Draw(img)

    draw.text((30, 22), "Iris: PRC vs K-Means / DBSCAN / HDBSCAN (ARI)", fill=(20, 20, 20))
    draw.line((margin_left, margin_top - 12, margin_left, height - margin_bottom), fill=(30, 30, 30), width=2)
    draw.line(
        (margin_left, height - margin_bottom, width - margin_right, height - margin_bottom),
        fill=(30, 30, 30),
        width=2,
    )
    for tick in range(0, 11):
        x = margin_left + int(axis_w * tick / 10)
        draw.line((x, margin_top - 8, x, height - margin_bottom), fill=(210, 210, 210), width=1)
        draw.text((x - 10, height - margin_bottom + 8), f"{tick/10:.1f}", fill=(60, 60, 60))

    palette = [(244, 162, 97), (42, 157, 143), (69, 123, 157), (231, 111, 81), (109, 89, 122)]
    y = margin_top
    for idx, row in enumerate(ok_rows):
        method = str(row["method"])
        ari = float(row["ari"])
        bar_w = int(axis_w * max(0.0, min(1.0, ari)))
        color = palette[idx % len(palette)]
        draw.text((30, y), method, fill=(30, 30, 30))
        draw.rectangle((margin_left, y + 10, margin_left + bar_w, y + 10 + bar_h), fill=color, outline=(0, 0, 0))
        draw.text((margin_left + bar_w + 8, y + 10), f"{ari:.3f}", fill=(40, 40, 40))
        y += row_height + bar_gap

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return True


def save_ari_plot(rows: Sequence[Dict[str, object]], out_path: Path) -> str:
    if _plot_ari_with_matplotlib(rows, out_path):
        return "matplotlib"
    if _plot_ari_with_pil(rows, out_path):
        return "pil"
    return "none"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare PRC/K-Means/DBSCAN/HDBSCAN on iris_all.txt")
    parser.add_argument("--data", type=Path, default=Path("datasets/iris/iris_all.txt"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--numpart", type=int, default=3)
    parser.add_argument("--prc-runs", type=int, default=10)
    parser.add_argument(
        "--baseline-input-space",
        choices=["raw", "standardized"],
        default="raw",
        help="Feature space used by baselines (default: raw, closer to C++ paper settings)",
    )
    parser.add_argument(
        "--prc-similarity",
        choices=["gauss", "knn"],
        default="gauss",
        help="PRC graph similarity type (C++ default: gauss)",
    )
    parser.add_argument(
        "--prc-dense",
        action="store_true",
        help="Use dense matrix for PRC (default: sparse)",
    )
    parser.add_argument("--kmeans-runs", type=int, default=20)
    parser.add_argument("--kmeans-max-iter", type=int, default=300)
    parser.add_argument("--dbscan-eps", type=float, default=0.75)
    parser.add_argument("--dbscan-min-samples", type=int, default=5)
    parser.add_argument("--hdbscan-min-cluster-size", type=int, default=5)
    parser.add_argument("--hdbscan-min-samples", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/experiments"))
    parser.add_argument("--csv-file", type=str, default="iris_compare_metrics.csv")
    parser.add_argument("--json-file", type=str, default="iris_compare_metrics.json")
    parser.add_argument("--plot-file", type=str, default="iris_compare_ari.png")
    parser.add_argument("--no-plot", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    x_raw, y_true = load_iris_from_file(args.data)
    x = standardize_features(x_raw) if args.baseline_input_space == "standardized" else x_raw

    rows: List[Dict[str, object]] = []

    labels_prc_pr = run_prc(
        data_file=args.data,
        num_partitions=args.numpart,
        seed=args.seed,
        num_init_orderings=args.prc_runs,
        metric=pyprc.PrcMetricEnum.PinchRatio,
        prc_similarity=args.prc_similarity,
        prc_use_sparse=(not args.prc_dense),
    )
    rows.append(summarize_result("PRC(PinchRatio)", labels_prc_pr, y_true))

    labels_prc_ncut = run_prc(
        data_file=args.data,
        num_partitions=args.numpart,
        seed=args.seed,
        num_init_orderings=args.prc_runs,
        metric=pyprc.PrcMetricEnum.NCut,
        prc_similarity=args.prc_similarity,
        prc_use_sparse=(not args.prc_dense),
    )
    rows.append(summarize_result("PRC(NCut)", labels_prc_ncut, y_true))

    labels_kmeans = run_kmeans(
        x=x,
        n_clusters=args.numpart,
        seed=args.seed,
        n_init=args.kmeans_runs,
        max_iter=args.kmeans_max_iter,
    )
    rows.append(summarize_result("K-Means", labels_kmeans, y_true))

    labels_dbscan = run_dbscan(x, eps=args.dbscan_eps, min_samples=args.dbscan_min_samples)
    rows.append(summarize_result("DBSCAN", labels_dbscan, y_true))

    labels_hdbscan, hdbscan_status = run_hdbscan_if_available(
        x,
        min_cluster_size=args.hdbscan_min_cluster_size,
        min_samples=args.hdbscan_min_samples,
    )
    rows.append(summarize_result("HDBSCAN", labels_hdbscan, y_true, extra_status=hdbscan_status))

    output_dir = args.output_dir
    csv_path = output_dir / args.csv_file
    json_path = output_dir / args.json_file
    plot_path = output_dir / args.plot_file

    save_csv(rows, csv_path)
    plot_backend = "skipped"
    if not args.no_plot:
        plot_backend = save_ari_plot(rows, plot_path)

    payload: Dict[str, object] = {
        "dataset": str(args.data),
        "seed": args.seed,
        "params": {
            "numpart": args.numpart,
            "prc_runs": args.prc_runs,
            "baseline_input_space": args.baseline_input_space,
            "prc_similarity": args.prc_similarity,
            "prc_use_sparse": (not args.prc_dense),
            "kmeans_runs": args.kmeans_runs,
            "kmeans_max_iter": args.kmeans_max_iter,
            "dbscan_eps": args.dbscan_eps,
            "dbscan_min_samples": args.dbscan_min_samples,
            "hdbscan_min_cluster_size": args.hdbscan_min_cluster_size,
            "hdbscan_min_samples": args.hdbscan_min_samples,
        },
        "plot_backend": plot_backend,
        "results": rows,
    }
    save_json(payload, json_path)

    print(f"[OK] CSV:  {csv_path}")
    print(f"[OK] JSON: {json_path}")
    if args.no_plot:
        print("[OK] Plot: skipped by --no-plot")
    else:
        print(f"[OK] Plot: {plot_path} (backend={plot_backend})")

    print("\nMethod comparison summary:")
    for row in rows:
        print(
            f"  - {row['method']:<16} "
            f"status={row['status']:<28} "
            f"ARI={row['ari']} NMI={row['nmi']} Purity={row['purity']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
