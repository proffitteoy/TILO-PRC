"""Reproduce PRC paper ARI figure (Iris + Vote) with diagnostics.

Usage:
    python experiments/reproduce_paper_fig_ari.py
    python experiments/reproduce_paper_fig_ari.py --use-paper-values
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import product
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pyprc


# ─── Data loading ───────────────────────────────────────────────────────────

def load_data_from_file(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    data = np.loadtxt(path, dtype=float)
    y_true = data[:, 0].astype(int)
    x = data[:, 1:].astype(float)
    return x, y_true


def resolve_vote_dataset_path(path: Path) -> Path:
    """Resolve vote dataset location without network download."""
    candidates = [path, REPO_ROOT / "house-votes-84.data", REPO_ROOT / "tests/vote_all.txt"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "vote dataset not found. Please provide --vote-data or place house-votes-84.data at repo root."
    )


def apply_vote_missing_strategy(x: np.ndarray, strategy: str) -> np.ndarray:
    """Re-encode cached vote features for different missing-value assumptions."""
    points = np.asarray(x, dtype=float).copy()
    missing = np.isclose(points, 0.5)

    if strategy == "half":
        return points
    if strategy == "zero":
        points[missing] = 0.0
        return points
    if strategy == "one":
        points[missing] = 1.0
        return points
    if strategy == "column_mode":
        for col_idx in range(points.shape[1]):
            col = points[:, col_idx]
            miss = np.isclose(col, 0.5)
            observed = col[~miss]
            if observed.size == 0:
                fill_value = 0.0
            else:
                fill_value = 1.0 if float(np.mean(observed)) >= 0.5 else 0.0
            col[miss] = fill_value
            points[:, col_idx] = col
        return points
    raise ValueError(f"unknown vote missing strategy: {strategy}")


def load_vote_data(path: Path, strategy: str) -> Tuple[np.ndarray, np.ndarray, int]:
    """Load vote dataset and apply missing-value strategy.

    Returns:
        x, y, removed_rows
    """
    raw_text = path.read_text(encoding="utf-8").strip()
    if not raw_text:
        raise ValueError(f"empty vote dataset: {path}")

    first_line = raw_text.splitlines()[0].strip()
    removed_rows = 0

    # UCI raw format: "republican,n,y,?,..."
    if "," in first_line:
        y_vals: List[int] = []
        x_vals: List[List[float]] = []
        for line in raw_text.splitlines():
            parts = [p.strip().lower() for p in line.strip().split(",")]
            if len(parts) < 2:
                continue
            label_name = parts[0]
            if label_name not in {"republican", "democrat"}:
                raise ValueError(f"unexpected vote label: {parts[0]!r}")
            feats = parts[1:]
            if strategy == "drop_rows" and any(v == "?" for v in feats):
                removed_rows += 1
                continue
            row: List[float] = []
            for token in feats:
                if token == "y":
                    row.append(1.0)
                elif token == "n":
                    row.append(0.0)
                elif token == "?":
                    row.append(0.5)
                else:
                    raise ValueError(f"unexpected vote token: {token!r}")
            y_vals.append(0 if label_name == "republican" else 1)
            x_vals.append(row)
        x_raw = np.asarray(x_vals, dtype=float)
        y_true = np.asarray(y_vals, dtype=int)
    else:
        x_raw, y_true = load_data_from_file(path)

    if strategy == "drop_rows":
        keep = ~np.any(np.isclose(x_raw, 0.5), axis=1)
        removed_rows += int(np.count_nonzero(~keep))
        x_raw = x_raw[keep]
        y_true = y_true[keep]
        return x_raw, y_true, removed_rows

    x_raw = apply_vote_missing_strategy(x_raw, strategy)
    return x_raw, y_true, removed_rows


def standardize(x: np.ndarray) -> np.ndarray:
    mu = np.mean(x, axis=0)
    sigma = np.std(x, axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    return (x - mu) / sigma


# ─── ARI computation ────────────────────────────────────────────────────────

def _contingency(a: Sequence[int], b: Sequence[int]) -> np.ndarray:
    ua = sorted(set(int(v) for v in a))
    ub = sorted(set(int(v) for v in b))
    ia = {v: i for i, v in enumerate(ua)}
    ib = {v: i for i, v in enumerate(ub)}
    table = np.zeros((len(ua), len(ub)), dtype=np.int64)
    for x, y in zip(a, b):
        table[ia[int(x)], ib[int(y)]] += 1
    return table


def adjusted_rand_index(true: Sequence[int], pred: Sequence[int]) -> float:
    n = len(true)
    if n <= 1:
        return 1.0
    table = _contingency(true, pred)
    comb2 = lambda x: x * (x - 1) // 2
    sum_nij = float(np.sum(comb2(table)))
    sum_ai = float(np.sum(comb2(np.sum(table, axis=1))))
    sum_bj = float(np.sum(comb2(np.sum(table, axis=0))))
    total = float(n * (n - 1) // 2)
    expected = (sum_ai * sum_bj) / total
    max_index = 0.5 * (sum_ai + sum_bj)
    denom = max_index - expected
    if abs(denom) < 1e-12:
        return 1.0
    return float((sum_nij - expected) / denom)


# ─── PRC helpers ────────────────────────────────────────────────────────────

def build_prc_matrix_from_points(
    points: np.ndarray,
    similarity: str = "gauss",
    use_sparse: bool = True,
    knn_k: int = -1,
    knn_mode: pyprc.KNNAdjMode = pyprc.KNNAdjMode.KNN_EITHER_ADJ_GAUSS,
    knn_sigma: float = -1.0,
    gauss_sigma: float = -1.0,
    gauss_mode: pyprc.GaussSimAdjMode = pyprc.GaussSimAdjMode.GS_ADJ_THRESHOLD,
    gauss_threshold: float = 1e-10,
) -> pyprc.MatrixStorage:
    if similarity == "knn":
        if use_sparse:
            matrix_like, _ = pyprc.knnSimSparseMatrix(points, knn_k, knn_mode, knn_sigma)
        else:
            matrix_like, _ = pyprc.knnSimMatrix(points, knn_k, knn_mode, knn_sigma)
    elif similarity == "gauss":
        if use_sparse:
            matrix_like, _ = pyprc.gaussSimSparseMatrix(points, gauss_sigma, gauss_mode, gauss_threshold)
        else:
            matrix_like, _ = pyprc.gaussSimMatrix(points, gauss_sigma, gauss_mode, gauss_threshold)
    else:
        raise ValueError(f"unknown PRC similarity type: {similarity}")
    return pyprc.MatrixStorage(matrix_like)


def order_from_labels(labels: Sequence[int], n: int, noise_last: bool = True) -> pyprc.OrderObject:
    if len(labels) != n:
        raise ValueError(f"init labels size mismatch: {len(labels)} vs {n}")
    buckets: Dict[int, List[int]] = {}
    for idx, lbl in enumerate(labels):
        buckets.setdefault(int(lbl), []).append(idx)
    if noise_last:
        keys = sorted(buckets.keys(), key=lambda k: (1 if k == -1 else 0, k))
    else:
        keys = sorted(buckets.keys())
    order_vec: List[int] = []
    for key in keys:
        order_vec.extend(buckets[key])
    return pyprc.OrderObject(data=order_vec)


def clone_prc_policy(
    policy: pyprc.PrcPolicyStruct,
    metric: Optional[pyprc.PrcMetricEnum] = None,
    prc_recurse_tilo: Optional[bool] = None,
    reverse_order_on_split: Optional[bool] = None,
    prc_return_recursive_order: Optional[bool] = None,
    prc_refine_tilo: Optional[bool] = None,
    tilo_max_iterations: Optional[int] = None,
) -> pyprc.PrcPolicyStruct:
    return pyprc.PrcPolicyStruct(
        tiloPolicy=pyprc.TiloPolicyStruct(
            maxIterations=policy.tiloPolicy.maxIterations
            if tilo_max_iterations is None
            else int(tilo_max_iterations),
            tiloEpsilon=policy.tiloPolicy.tiloEpsilon,
        ),
        metric=policy.metric if metric is None else metric,
        prcRecurseTILO=policy.prcRecurseTILO if prc_recurse_tilo is None else bool(prc_recurse_tilo),
        reverseOrderOnSplit=policy.reverseOrderOnSplit
        if reverse_order_on_split is None
        else bool(reverse_order_on_split),
        prcReturnRecursiveOrder=policy.prcReturnRecursiveOrder
        if prc_return_recursive_order is None
        else bool(prc_return_recursive_order),
        prcRefineTILO=policy.prcRefineTILO if prc_refine_tilo is None else bool(prc_refine_tilo),
        prcEvalAllMetrics=policy.prcEvalAllMetrics,
        prcReturnMetrics=policy.prcReturnMetrics,
    )


def _run_tilo_variant_best_of_trials(
    matrix: pyprc.MatrixStorage,
    num_partitions: int,
    policy_template: pyprc.PrcPolicyStruct,
    metric: pyprc.PrcMetricEnum,
    n_trials: int,
    seed_start: int,
) -> np.ndarray:
    policy = clone_prc_policy(policy_template, metric=metric)
    best_labels: Optional[np.ndarray] = None
    best_counts: Optional[pyprc.PrcReturnStruct] = None
    best_boundary: List[float] = []
    for trial in range(n_trials):
        pyprc._GLOBAL_C_RAND.srand(seed_start + trial + 1)
        order = pyprc.initOrder_random(matrix.rows())
        counts, labels = pyprc.pinchRatioClustering_storage(matrix, order, num_partitions, policy)
        boundary = sorted(order.boundary().data(), reverse=True)
        if best_labels is None:
            best_labels = labels.copy()
            best_counts = counts
            best_boundary = list(boundary)
            continue
        if pyprc.cless(counts, best_counts, boundary, best_boundary):  # type: ignore[arg-type]
            best_labels = labels.copy()
            best_counts = counts
            best_boundary = list(boundary)
    if best_labels is None:
        raise RuntimeError("TILO/PRC returned no labels")
    return best_labels


def collect_tilo_trial_ari_stats(
    matrix: pyprc.MatrixStorage,
    y_true: np.ndarray,
    num_partitions: int,
    policy_template: pyprc.PrcPolicyStruct,
    metric: pyprc.PrcMetricEnum,
    n_trials: int,
    seed_start: int,
) -> Dict[str, float]:
    policy = clone_prc_policy(policy_template, metric=metric)
    aris: List[float] = []
    for trial in range(n_trials):
        pyprc._GLOBAL_C_RAND.srand(seed_start + trial + 1)
        order = pyprc.initOrder_random(matrix.rows())
        _, labels = pyprc.pinchRatioClustering_storage(matrix, order, num_partitions, policy)
        aris.append(adjusted_rand_index(y_true.tolist(), labels.tolist()))
    return {
        "min": round(float(np.min(aris)), 6),
        "mean": round(float(np.mean(aris)), 6),
        "max": round(float(np.max(aris)), 6),
    }


def run_tilo_prc(
    matrix: pyprc.MatrixStorage,
    num_partitions: int,
    policy_template: pyprc.PrcPolicyStruct,
    n_trials: int = 20,
    seed_start: int = 1,
) -> np.ndarray:
    return _run_tilo_variant_best_of_trials(
        matrix=matrix,
        num_partitions=num_partitions,
        policy_template=policy_template,
        metric=pyprc.PrcMetricEnum.PinchRatio,
        n_trials=n_trials,
        seed_start=seed_start,
    )


def run_tilo_ncut(
    matrix: pyprc.MatrixStorage,
    num_partitions: int,
    policy_template: pyprc.PrcPolicyStruct,
    n_trials: int = 20,
    seed_start: int = 1,
) -> np.ndarray:
    return _run_tilo_variant_best_of_trials(
        matrix=matrix,
        num_partitions=num_partitions,
        policy_template=policy_template,
        metric=pyprc.PrcMetricEnum.NCut,
        n_trials=n_trials,
        seed_start=seed_start,
    )


def run_prc_from_init(
    matrix: pyprc.MatrixStorage,
    num_partitions: int,
    init_labels: Sequence[int],
    policy_template: pyprc.PrcPolicyStruct,
    noise_last: bool = True,
    preserve_init_effect: bool = False,
) -> np.ndarray:
    init_labels_arr = np.asarray(init_labels, dtype=int)
    if preserve_init_effect:
        # Keep initialization influence visible by disabling recursive/refine passes.
        policy = clone_prc_policy(
            policy_template,
            metric=pyprc.PrcMetricEnum.PinchRatio,
            prc_recurse_tilo=False,
            reverse_order_on_split=False,
            prc_return_recursive_order=False,
            prc_refine_tilo=False,
            tilo_max_iterations=1,
        )
    else:
        policy = clone_prc_policy(policy_template, metric=pyprc.PrcMetricEnum.PinchRatio)
    order = order_from_labels(init_labels, matrix.rows(), noise_last=noise_last)
    try:
        _, labels = pyprc.pinchRatioClustering_storage(matrix, order, num_partitions, policy)
    except Exception:
        if preserve_init_effect:
            return init_labels_arr.copy()
        raise
    return labels


# ─── Baseline clustering methods ───────────────────────────────────────────

def _param_grid(grid: Dict[str, Sequence[Any]]) -> Iterable[Dict[str, Any]]:
    keys = list(grid.keys())
    for values in product(*(grid[k] for k in keys)):
        yield dict(zip(keys, values))


def _search_best_labels(
    x: np.ndarray,
    y_true: np.ndarray,
    runner: Callable[[np.ndarray, Dict[str, Any]], np.ndarray],
    grid: Dict[str, Sequence[Any]],
) -> Tuple[np.ndarray, Dict[str, Any], float]:
    best_labels: Optional[np.ndarray] = None
    best_params: Dict[str, Any] = {}
    best_ari = -1.0
    for params in _param_grid(grid):
        try:
            labels = runner(x, params)
        except Exception:
            continue
        ari = adjusted_rand_index(y_true.tolist(), labels.tolist())
        if ari > best_ari:
            best_ari = ari
            best_labels = labels
            best_params = params
    if best_labels is None:
        raise RuntimeError("parameter search failed for one baseline")
    return best_labels, best_params, best_ari


def _pairwise_dist2(x: np.ndarray, y: Optional[np.ndarray] = None) -> np.ndarray:
    other = x if y is None else y
    diff = x[:, None, :] - other[None, :, :]
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


def _kmeans_fallback(
    x: np.ndarray,
    n_clusters: int,
    seed: int,
    n_init: int,
    max_iter: int = 300,
    tol: float = 1e-6,
) -> np.ndarray:
    n = x.shape[0]
    best_labels: Optional[np.ndarray] = None
    best_inertia = float("inf")
    base_rng = np.random.default_rng(seed)
    seeds = base_rng.integers(0, 2**31 - 1, size=max(1, n_init), endpoint=False)

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
        raise RuntimeError("K-Means fallback failed to produce labels.")
    return best_labels


def run_kmeans(x: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    try:
        from sklearn.cluster import KMeans  # type: ignore

        return KMeans(
            n_clusters=int(params["n_clusters"]),
            random_state=int(params["seed"]),
            n_init=int(params["n_init"]),
        ).fit_predict(x)
    except Exception:
        return _kmeans_fallback(
            x,
            n_clusters=int(params["n_clusters"]),
            seed=int(params["seed"]),
            n_init=int(params["n_init"]),
        )


def _spectral_fallback(x: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    n = x.shape[0]
    k = int(params["n_clusters"])
    affinity = str(params["affinity"])

    if affinity == "nearest_neighbors":
        n_neighbors = max(1, min(int(params["n_neighbors"]), n - 1))
        dist2 = _pairwise_dist2(x)
        np.fill_diagonal(dist2, np.inf)
        nn = np.argpartition(dist2, kth=n_neighbors - 1, axis=1)[:, :n_neighbors]
        a = np.zeros((n, n), dtype=float)
        for i in range(n):
            a[i, nn[i]] = 1.0
        a = np.maximum(a, a.T)
    else:
        gamma = float(params["gamma"])
        dist2 = _pairwise_dist2(x)
        a = np.exp(-gamma * dist2)
        np.fill_diagonal(a, 0.0)

    d = np.sum(a, axis=1)
    d_safe = np.where(d <= 1e-12, 1.0, d)
    d_inv_sqrt = 1.0 / np.sqrt(d_safe)
    lap = np.eye(n) - (d_inv_sqrt[:, None] * a) * d_inv_sqrt[None, :]
    _, eigvecs = np.linalg.eigh(lap)
    u = eigvecs[:, :k]
    row_norm = np.linalg.norm(u, axis=1, keepdims=True)
    row_norm[row_norm <= 1e-12] = 1.0
    u_norm = u / row_norm
    return _kmeans_fallback(
        u_norm,
        n_clusters=k,
        seed=int(params["seed"]),
        n_init=20,
    )


def run_spectral(x: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    try:
        from sklearn.cluster import SpectralClustering  # type: ignore

        affinity = str(params["affinity"])
        kwargs: Dict[str, Any] = {
            "n_clusters": int(params["n_clusters"]),
            "random_state": int(params["seed"]),
            "affinity": affinity,
            "assign_labels": str(params["assign_labels"]),
        }
        if affinity == "nearest_neighbors":
            kwargs["n_neighbors"] = int(params["n_neighbors"])
        else:
            kwargs["gamma"] = float(params["gamma"])
        return SpectralClustering(**kwargs).fit_predict(x)
    except Exception:
        return _spectral_fallback(x, params)


def _dbscan_fallback(x: np.ndarray, eps: float, min_samples: int) -> np.ndarray:
    n = x.shape[0]
    dist = np.sqrt(_pairwise_dist2(x))
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


def run_dbscan(x: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    eps = float(params["eps"])
    min_samples = int(params["min_samples"])
    try:
        from sklearn.cluster import DBSCAN  # type: ignore

        return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(x)
    except Exception:
        return _dbscan_fallback(x, eps=eps, min_samples=min_samples)


def _affinity_propagation_fallback(
    x: np.ndarray,
    damping: float,
    preference: Optional[float],
    max_iter: int = 200,
    convergence_iter: int = 15,
) -> np.ndarray:
    n = x.shape[0]
    s = -_pairwise_dist2(x)
    pref = float(np.median(s)) if preference is None else float(preference)
    np.fill_diagonal(s, pref)

    r = np.zeros((n, n), dtype=float)
    a = np.zeros((n, n), dtype=float)
    e_hist = np.zeros((convergence_iter, n), dtype=bool)
    diag_idx = np.arange(n)

    for it in range(max_iter):
        as_sum = a + s
        max_idx = np.argmax(as_sum, axis=1)
        max_val = as_sum[diag_idx, max_idx]
        as_copy = as_sum.copy()
        as_copy[diag_idx, max_idx] = -np.inf
        second_max = np.max(as_copy, axis=1)

        r_new = s - max_val[:, None]
        r_new[diag_idx, max_idx] = s[diag_idx, max_idx] - second_max
        r = damping * r + (1.0 - damping) * r_new

        rp = np.maximum(r, 0.0)
        rp[diag_idx, diag_idx] = r[diag_idx, diag_idx]
        a_new = np.sum(rp, axis=0)[None, :] - rp
        a_new = np.minimum(a_new, 0.0)
        a_new[diag_idx, diag_idx] = np.sum(rp, axis=0) - rp[diag_idx, diag_idx]
        a = damping * a + (1.0 - damping) * a_new

        exemplars = np.diag(a + r) > 0
        e_hist[it % convergence_iter, :] = exemplars
        if it >= convergence_iter:
            k = np.sum(e_hist, axis=0)
            if np.all((k == 0) | (k == convergence_iter)):
                break

    exemplar_ids = np.where(np.diag(a + r) > 0)[0]
    if exemplar_ids.size == 0:
        exemplar_ids = np.array([int(np.argmax(np.diag(a + r)))], dtype=int)
    sim = s[:, exemplar_ids]
    chosen = exemplar_ids[np.argmax(sim, axis=1)]
    _, labels = np.unique(chosen, return_inverse=True)
    return labels.astype(int)


def run_affinity_propagation(x: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    preference = params["preference"]
    if preference is None:
        pref_value = None
    elif preference == "median":
        sim = -np.sum((x[:, None, :] - x[None, :, :]) ** 2, axis=2)
        pref_value = float(np.median(sim))
    else:
        pref_value = float(preference)

    damping = float(params["damping"])
    seed = int(params["seed"])
    try:
        from sklearn.cluster import AffinityPropagation  # type: ignore

        return AffinityPropagation(
            random_state=seed,
            damping=damping,
            preference=pref_value,
        ).fit_predict(x)
    except Exception:
        np.random.seed(seed)
        return _affinity_propagation_fallback(x, damping=damping, preference=pref_value)


def _estimate_bandwidth_quantile(x: np.ndarray, quantile: float, n_samples: int, seed: int = 0) -> float:
    n = x.shape[0]
    m = max(2, min(int(n_samples), n))
    rng = np.random.default_rng(seed)
    idx = rng.choice(n, size=m, replace=False)
    sample = x[idx]
    dist = np.sqrt(_pairwise_dist2(sample))
    tri = dist[np.triu_indices(m, k=1)]
    if tri.size == 0:
        return 1.0
    bw = float(np.quantile(tri, min(max(quantile, 0.01), 0.99)))
    if bw <= 1e-12:
        bw = float(np.mean(tri))
    return max(bw, 1e-6)


def _mean_shift_fallback(
    x: np.ndarray,
    bandwidth: Optional[float],
    bin_seeding: bool,
    max_iter: int = 100,
    tol: float = 1e-3,
) -> np.ndarray:
    if bandwidth is None or bandwidth <= 1e-12:
        bandwidth = _estimate_bandwidth_quantile(x, quantile=0.2, n_samples=min(500, x.shape[0]))
    bw = float(max(bandwidth, 1e-6))
    bw2 = bw * bw

    seeds = x.copy()
    if bin_seeding and x.shape[0] > 1:
        step = max(1, int(round(bw)))
        seeds = x[::step].copy()

    centers: List[np.ndarray] = []
    for seed in seeds:
        center = seed.copy()
        for _ in range(max_iter):
            dist2 = np.sum((x - center) ** 2, axis=1)
            members = x[dist2 <= bw2]
            if members.shape[0] == 0:
                break
            new_center = np.mean(members, axis=0)
            if float(np.linalg.norm(new_center - center)) <= tol * bw:
                center = new_center
                break
            center = new_center

        merged = False
        for idx, existing in enumerate(centers):
            if float(np.linalg.norm(center - existing)) <= bw * 0.5:
                centers[idx] = 0.5 * (existing + center)
                merged = True
                break
        if not merged:
            centers.append(center)

    if not centers:
        return np.zeros(x.shape[0], dtype=int)
    center_arr = np.asarray(centers, dtype=float)
    labels = np.argmin(_pairwise_dist2(x, center_arr), axis=1)
    return labels.astype(int)


def run_mean_shift(x: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    bandwidth = params["bandwidth"]
    quantile = float(params["quantile"])
    n_samples = min(int(params["n_samples"]), x.shape[0])
    bin_seeding = bool(params["bin_seeding"])

    try:
        from sklearn.cluster import MeanShift, estimate_bandwidth  # type: ignore

        if bandwidth == "auto_q":
            bandwidth_value = float(estimate_bandwidth(x, quantile=quantile, n_samples=n_samples))
            if bandwidth_value <= 1e-12:
                bandwidth_value = None
        elif bandwidth is None:
            bandwidth_value = None
        else:
            bandwidth_value = float(bandwidth)
        return MeanShift(bandwidth=bandwidth_value, bin_seeding=bin_seeding).fit_predict(x)
    except Exception:
        if bandwidth == "auto_q":
            bandwidth_value = _estimate_bandwidth_quantile(x, quantile=quantile, n_samples=n_samples, seed=0)
        elif bandwidth is None:
            bandwidth_value = None
        else:
            bandwidth_value = float(bandwidth)
        return _mean_shift_fallback(x, bandwidth=bandwidth_value, bin_seeding=bin_seeding)


# ─── Run all methods for one dataset ───────────────────────────────────────

def run_all_methods(
    data_file: Path,
    num_partitions: int,
    seed: int,
    dbscan_eps: float,
    dbscan_min_samples: int,
    n_trials: int = 20,
    dataset_name: str = "",
    use_standardized_for_prc: bool = False,
    baseline_input_space: str = "raw",
    prc_similarity: str = "gauss",
    prc_use_sparse: bool = True,
    tune_baselines: bool = False,
    prc_policy_template: Optional[pyprc.PrcPolicyStruct] = None,
    prc_noise_last: bool = False,
    vote_missing_strategy: str = "drop_rows",
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    vote_removed_rows = 0
    if dataset_name.lower() == "vote":
        x_raw, y_true, vote_removed_rows = load_vote_data(data_file, vote_missing_strategy)
    else:
        x_raw, y_true = load_data_from_file(data_file)
    x_std = standardize(x_raw)
    baseline_x = x_std if baseline_input_space == "standardized" else x_raw
    prc_points = x_std if use_standardized_for_prc else x_raw
    policy_template = prc_policy_template or pyprc.PrcPolicyStruct(metric=pyprc.PrcMetricEnum.PinchRatio)
    matrix = build_prc_matrix_from_points(
        prc_points,
        similarity=prc_similarity,
        use_sparse=prc_use_sparse,
    )

    results: Dict[str, float] = {}
    details: Dict[str, Any] = {"baseline_params": {}, "notes": []}

    # TILO-NCUT / TILO-PRC standalone
    details["tilo_trial_ari"] = {
        "NCUT": collect_tilo_trial_ari_stats(
            matrix=matrix,
            y_true=y_true,
            num_partitions=num_partitions,
            policy_template=policy_template,
            metric=pyprc.PrcMetricEnum.NCut,
            n_trials=n_trials,
            seed_start=seed,
        ),
        "PRC": collect_tilo_trial_ari_stats(
            matrix=matrix,
            y_true=y_true,
            num_partitions=num_partitions,
            policy_template=policy_template,
            metric=pyprc.PrcMetricEnum.PinchRatio,
            n_trials=n_trials,
            seed_start=seed,
        ),
    }
    labels_ncut = run_tilo_ncut(
        matrix,
        num_partitions,
        policy_template=policy_template,
        n_trials=n_trials,
        seed_start=seed,
    )
    results["TILO-NCUT"] = adjusted_rand_index(y_true.tolist(), labels_ncut.tolist())
    labels_prc = run_tilo_prc(
        matrix,
        num_partitions,
        policy_template=policy_template,
        n_trials=n_trials,
        seed_start=seed,
    )
    results["TILO-PRC"] = adjusted_rand_index(y_true.tolist(), labels_prc.tolist())

    # KMeans
    if tune_baselines:
        km_grid = {
            "n_clusters": [num_partitions],
            "seed": [seed],
            "n_init": [10, 20, 50],
        }
        labels_km, km_params, _ = _search_best_labels(baseline_x, y_true, run_kmeans, km_grid)
    else:
        km_params = {"n_clusters": num_partitions, "seed": seed, "n_init": 20}
        labels_km = run_kmeans(baseline_x, km_params)
    details["baseline_params"]["K Means"] = km_params
    results["K Means"] = adjusted_rand_index(y_true.tolist(), labels_km.tolist())
    results["TILO-PRC(K Means)"] = adjusted_rand_index(
        y_true.tolist(),
        run_prc_from_init(
            matrix,
            num_partitions,
            labels_km.tolist(),
            policy_template=policy_template,
            noise_last=prc_noise_last,
        ).tolist(),
    )

    # Spectral
    if tune_baselines:
        sp_grid = {
            "n_clusters": [num_partitions],
            "seed": [seed],
            "affinity": ["nearest_neighbors", "rbf"],
            "n_neighbors": [5, 10, 15],
            "gamma": [0.25, 0.5, 1.0],
            "assign_labels": ["kmeans", "discretize"],
        }
        labels_sp, sp_params, _ = _search_best_labels(baseline_x, y_true, run_spectral, sp_grid)
    else:
        sp_params = {
            "n_clusters": num_partitions,
            "seed": seed,
            "affinity": "nearest_neighbors",
            "n_neighbors": 10,
            "gamma": 1.0,
            "assign_labels": "kmeans",
        }
        labels_sp = run_spectral(baseline_x, sp_params)
    details["baseline_params"]["Spectral"] = sp_params
    results["Spectral"] = adjusted_rand_index(y_true.tolist(), labels_sp.tolist())
    results["TILO-PRC(Spectral)"] = adjusted_rand_index(
        y_true.tolist(),
        run_prc_from_init(
            matrix,
            num_partitions,
            labels_sp.tolist(),
            policy_template=policy_template,
            noise_last=prc_noise_last,
        ).tolist(),
    )

    # DBSCAN
    if tune_baselines:
        eps_base = float(dbscan_eps)
        db_grid = {
            "eps": [max(0.05, eps_base * 0.6), eps_base, eps_base * 1.25, eps_base * 1.6],
            "min_samples": [max(2, dbscan_min_samples - 2), dbscan_min_samples, dbscan_min_samples + 2],
        }
        labels_db, db_params, _ = _search_best_labels(baseline_x, y_true, run_dbscan, db_grid)
    else:
        db_params = {"eps": dbscan_eps, "min_samples": dbscan_min_samples}
        labels_db = run_dbscan(baseline_x, db_params)
    details["baseline_params"]["DBScan"] = db_params
    results["DBScan"] = adjusted_rand_index(y_true.tolist(), labels_db.tolist())
    results["TILO-PRC(DBScan)"] = adjusted_rand_index(
        y_true.tolist(),
        run_prc_from_init(
            matrix,
            num_partitions,
            labels_db.tolist(),
            policy_template=policy_template,
            noise_last=prc_noise_last,
        ).tolist(),
    )

    # Affinity Propagation
    if tune_baselines:
        ap_grid = {
            "seed": [seed],
            "damping": [0.7, 0.8, 0.9, 0.95],
            "preference": [None, "median"],
        }
        labels_ap, ap_params, _ = _search_best_labels(baseline_x, y_true, run_affinity_propagation, ap_grid)
    else:
        ap_params = {"seed": seed, "damping": 0.9, "preference": None}
        labels_ap = run_affinity_propagation(baseline_x, ap_params)
    details["baseline_params"]["Aff. Prop."] = ap_params
    results["Aff. Prop."] = adjusted_rand_index(y_true.tolist(), labels_ap.tolist())
    results["TILO-PRC(Aff. Prop.)"] = adjusted_rand_index(
        y_true.tolist(),
        run_prc_from_init(
            matrix,
            num_partitions,
            labels_ap.tolist(),
            policy_template=policy_template,
            noise_last=prc_noise_last,
        ).tolist(),
    )

    # Mean Shift
    if tune_baselines:
        ms_grid = {
            "bandwidth": [None, "auto_q"],
            "quantile": [0.15, 0.2, 0.25, 0.3],
            "n_samples": [200, 500],
            "bin_seeding": [False, True],
        }
        labels_ms, ms_params, _ = _search_best_labels(baseline_x, y_true, run_mean_shift, ms_grid)
    else:
        ms_params = {"bandwidth": None, "quantile": 0.2, "n_samples": 500, "bin_seeding": False}
        labels_ms = run_mean_shift(baseline_x, ms_params)
    details["baseline_params"]["Mean Shift"] = ms_params
    results["Mean Shift"] = adjusted_rand_index(y_true.tolist(), labels_ms.tolist())
    results["TILO-PRC(Mean Shift)"] = adjusted_rand_index(
        y_true.tolist(),
        run_prc_from_init(
            matrix,
            num_partitions,
            labels_ms.tolist(),
            policy_template=policy_template,
            noise_last=prc_noise_last,
        ).tolist(),
    )

    details["prc_policy"] = {
        "recurse_tilo": bool(policy_template.prcRecurseTILO),
        "reverse_order_on_split": bool(policy_template.reverseOrderOnSplit),
        "return_recursive_order": bool(policy_template.prcReturnRecursiveOrder),
        "refine_tilo": bool(policy_template.prcRefineTILO),
        "eval_all_metrics": bool(policy_template.prcEvalAllMetrics),
        "return_metrics": bool(policy_template.prcReturnMetrics),
        "tilo_max_iterations": int(policy_template.tiloPolicy.maxIterations),
        "tilo_epsilon": float(policy_template.tiloPolicy.tiloEpsilon),
    }
    if dataset_name.lower() == "vote":
        details["vote_missing_strategy"] = vote_missing_strategy
        details["vote_removed_rows"] = vote_removed_rows
        details["vote_rows_after_filter"] = int(x_raw.shape[0])
    details["notes"].append(
        f"PRC input space = {'standardized' if use_standardized_for_prc else 'raw'}; "
        f"PRC similarity = {prc_similarity}; PRC sparse = {prc_use_sparse}; "
        f"baseline input space = {baseline_input_space}; "
        f"tune_baselines={tune_baselines}; prc_noise_last={prc_noise_last}; "
        "preserve_init_diff_for_kmeans_dbscan_spectral=False; "
        f"vote_missing_strategy={vote_missing_strategy if dataset_name.lower() == 'vote' else 'n/a'}"
    )
    return results, details


# ─── Plotting ───────────────────────────────────────────────────────────────

def plot_paper_figure(
    iris_results: Dict[str, float],
    vote_results: Dict[str, float],
    out_path: Path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.ticker import MultipleLocator

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Computer Modern Roman", "Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "cm",
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
        }
    )

    method_pairs = [
        ("K Means", "TILO-PRC(K Means)"),
        ("Spectral", "TILO-PRC(Spectral)"),
        ("DBScan", "TILO-PRC(DBScan)"),
        ("Aff. Prop.", "TILO-PRC(Aff. Prop.)"),
        ("Mean Shift", "TILO-PRC(Mean Shift)"),
    ]

    color_ncut = "#003399"
    color_prc = "#99CCFF"
    color_other = "#8B0000"
    color_prc_init = "#FF8C00"

    def make_subplot(ax, results: Dict[str, float], title: str) -> None:
        bar_width = 0.6
        gap_within_pair = 0.15
        gap_between_groups = 0.8

        positions: List[float] = []
        values: List[float] = []
        colors: List[str] = []
        tick_positions: List[float] = []
        tick_labels: List[str] = []
        pos = 0.0

        positions.append(pos)
        values.append(results.get("TILO-NCUT", 0.0))
        colors.append(color_ncut)
        tick_positions.append(pos)
        tick_labels.append("TILO-\nNCUT")
        pos += bar_width + gap_within_pair

        positions.append(pos)
        values.append(results.get("TILO-PRC", 0.0))
        colors.append(color_prc)
        tick_positions.append(pos)
        tick_labels.append("TILO-\nPRC")
        pos += bar_width + gap_between_groups

        for other_name, prc_name in method_pairs:
            positions.append(pos)
            values.append(results.get(other_name, 0.0))
            colors.append(color_other)
            p1 = pos
            pos += bar_width + gap_within_pair

            positions.append(pos)
            values.append(results.get(prc_name, 0.0))
            colors.append(color_prc_init)
            p2 = pos

            tick_positions.append((p1 + p2) / 2)
            tick_labels.append(other_name.replace(" ", "\n") if len(other_name) > 6 else other_name)
            pos += bar_width + gap_between_groups

        ax.bar(positions, values, width=bar_width, color=colors, edgecolor="none")
        ax.set_ylabel("Adjusted Rand Index", fontsize=10)
        ax.set_ylim(0.0, 1.0)
        ax.set_yticks(np.arange(0, 1.1, 0.2))
        ax.yaxis.set_minor_locator(MultipleLocator(0.1))
        ax.set_xlim(-0.5, pos - gap_between_groups + bar_width + 0.3)
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, fontsize=8, ha="center")
        ax.grid(True, axis="y", which="major", linestyle="-", linewidth=0.4, alpha=0.5)
        ax.grid(True, axis="y", which="minor", linestyle=":", linewidth=0.3, alpha=0.4)
        ax.set_axisbelow(True)
        ax.set_title(title, fontsize=11, pad=8)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    make_subplot(ax1, iris_results, "(a) Iris")
    make_subplot(ax2, vote_results, "(b) Vote")

    legend_handles = [
        Patch(facecolor=color_ncut, label="TILO with Normalized Cut"),
        Patch(facecolor=color_prc, label="TILO with Pinch Ratio"),
        Patch(facecolor=color_other, label="Other method"),
        Patch(facecolor=color_prc_init, label="TILO-PRC initialized with other method"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=4,
        frameon=False,
        fontsize=9,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved figure: {out_path}")


# ─── Paper reference values (read from figure) ────────────────────────────

PAPER_REFERENCE_NOTE = (
    "Approximate ARI values digitized from the provided paper figure image and "
    "rounded to 2 decimals."
)

PAPER_IRIS_ARI = {
    "TILO-NCUT": 0.62,
    "TILO-PRC": 0.90,
    "K Means": 0.73,
    "TILO-PRC(K Means)": 0.90,
    "Spectral": 0.79,
    "TILO-PRC(Spectral)": 0.90,
    "DBScan": 0.51,
    "TILO-PRC(DBScan)": 0.90,
    "Aff. Prop.": 0.54,
    "TILO-PRC(Aff. Prop.)": 0.90,
    "Mean Shift": 0.57,
    "TILO-PRC(Mean Shift)": 0.90,
}

PAPER_VOTE_ARI = {
    "TILO-NCUT": 0.52,
    "TILO-PRC": 0.82,
    "K Means": 0.54,
    "TILO-PRC(K Means)": 0.82,
    "Spectral": 0.69,
    "TILO-PRC(Spectral)": 0.82,
    "DBScan": 0.01,
    "TILO-PRC(DBScan)": 0.82,
    "Aff. Prop.": 0.09,
    "TILO-PRC(Aff. Prop.)": 0.82,
    "Mean Shift": 0.00,
    "TILO-PRC(Mean Shift)": 0.82,
}


def calc_delta_to_paper(results: Dict[str, float], paper: Dict[str, float]) -> Dict[str, float]:
    keys = sorted(set(results.keys()) & set(paper.keys()))
    return {k: round(results[k] - paper[k], 6) for k in keys}


# ─── Main ───────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reproduce paper ARI comparison figure with diagnostics")
    p.add_argument("--iris-data", type=Path, default=Path("tests/iris_all.txt"))
    p.add_argument("--vote-data", type=Path, default=Path("house-votes-84.data"))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--iris-k", type=int, default=3)
    p.add_argument("--vote-k", type=int, default=2)
    p.add_argument("--iris-dbscan-eps", type=float, default=0.75)
    p.add_argument("--iris-dbscan-min-samples", type=int, default=5)
    p.add_argument("--vote-dbscan-eps", type=float, default=1.5)
    p.add_argument("--vote-dbscan-min-samples", type=int, default=5)
    p.add_argument("--n-trials", type=int, default=20)
    p.add_argument("--output", type=Path, default=Path("experiments/output/paper_fig_ari_comparison.png"))
    p.add_argument("--diagnostics", type=Path, default=Path("experiments/output/paper_fig_ari_diagnostics.json"))
    p.add_argument("--no-plot", action="store_true", help="Skip figure generation")
    p.add_argument("--use-paper-values", action="store_true", help="Use hardcoded paper ARI values for visual reference")
    p.add_argument(
        "--paper-profile",
        action="store_true",
        help="Apply a historical C++/paper-like PRC configuration profile where the repository has evidence.",
    )
    p.add_argument(
        "--prc-input-space",
        choices=["standardized", "raw"],
        default="raw",
        help="Space used to build PRC graph (paper-like default: raw)",
    )
    p.add_argument(
        "--baseline-input-space",
        choices=["standardized", "raw"],
        default="raw",
        help="Feature space used by baseline methods (paper-like default: raw)",
    )
    p.add_argument(
        "--prc-similarity",
        choices=["gauss", "knn"],
        default="gauss",
        help="Graph builder for PRC (paper C++ default: gauss)",
    )
    p.add_argument(
        "--prc-dense",
        action="store_true",
        help="Use dense matrix for PRC graph (default is sparse, like original C++ runs)",
    )
    p.add_argument("--tune-baselines", action="store_true", help="Enable baseline hyper-parameter search")
    p.add_argument("--no-tune-baselines", action="store_true", help="Force disable baseline hyper-parameter search")
    p.add_argument("--prc-noise-first", action="store_true", help="Put noise label (-1) at start when converting labels to init order")
    p.add_argument("--prc-noise-last", action="store_true", help="Put noise label (-1) at end when converting labels to init order")
    p.add_argument("--prc-recurse-tilo", action="store_true", help="Re-run TILO after each PRC split.")
    p.add_argument("--reverse-order-on-split", action="store_true", help="Reverse the second partition when splitting recursively.")
    p.add_argument("--prc-return-recursive-order", action="store_true", help="Write back the recursively refined order.")
    p.add_argument("--prc-refine-tilo", action="store_true", help="Run RefineTILO after each TILO step.")
    p.add_argument(
        "--vote-missing-strategy",
        choices=["drop_rows", "half", "zero", "one", "column_mode"],
        default="drop_rows",
        help="How to handle vote missing values ('drop_rows' follows the paper preprocessing note).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.paper_profile:
        args.prc_input_space = "raw"
        args.baseline_input_space = "raw"
        args.prc_similarity = "gauss"
        args.prc_dense = False
        # Historical C++ test scripts exercise this as the most complete PRC/TILO path.
        args.prc_recurse_tilo = True
        args.reverse_order_on_split = True
        args.prc_return_recursive_order = True
        args.prc_refine_tilo = True

    if args.use_paper_values:
        print("Using hardcoded paper ARI values for visual reference only.")
        iris_results = PAPER_IRIS_ARI
        vote_results = PAPER_VOTE_ARI
        diagnostics_payload = {
            "mode": "paper-values",
            "note": "No experiment executed.",
            "paper_reference_note": PAPER_REFERENCE_NOTE,
            "paper_reference": {
                "iris": PAPER_IRIS_ARI,
                "vote": PAPER_VOTE_ARI,
            },
        }
    else:
        args.vote_data = resolve_vote_dataset_path(args.vote_data)
        use_std_for_prc = args.prc_input_space == "standardized"
        tune_baselines = bool(args.tune_baselines and not args.no_tune_baselines)
        # C++ initLabelsFile behavior (std::map key order) puts -1 first by default.
        noise_last = bool(args.prc_noise_last and not args.prc_noise_first)
        prc_use_sparse = not args.prc_dense
        prc_policy_template = pyprc.PrcPolicyStruct(
            metric=pyprc.PrcMetricEnum.PinchRatio,
            prcRecurseTILO=bool(args.prc_recurse_tilo),
            reverseOrderOnSplit=bool(args.reverse_order_on_split),
            prcReturnRecursiveOrder=bool(args.prc_return_recursive_order),
            prcRefineTILO=bool(args.prc_refine_tilo),
        )
        if use_std_for_prc or args.baseline_input_space == "standardized" or args.prc_similarity != "gauss":
            print(
                "[WARN] 当前配置偏离原始 C++ 默认协议（raw + gauss + sparse）。"
                "这通常会显著改变 ARI，尤其是 Iris 上 TILO-PRC。"
            )

        print(
            f"Running Iris (n_trials={args.n_trials}, prc_input={args.prc_input_space}, "
            f"baseline_input={args.baseline_input_space}, prc_similarity={args.prc_similarity}, "
            f"prc_sparse={prc_use_sparse}, tune_baselines={tune_baselines})..."
        )
        iris_results, iris_details = run_all_methods(
            args.iris_data,
            args.iris_k,
            args.seed,
            args.iris_dbscan_eps,
            args.iris_dbscan_min_samples,
            n_trials=args.n_trials,
            dataset_name="iris",
            use_standardized_for_prc=use_std_for_prc,
            baseline_input_space=args.baseline_input_space,
            prc_similarity=args.prc_similarity,
            prc_use_sparse=prc_use_sparse,
            tune_baselines=tune_baselines,
            prc_policy_template=prc_policy_template,
            prc_noise_last=noise_last,
        )
        print("Iris ARI results:")
        for k, v in iris_results.items():
            print(f"  {k:<25} ARI={v:.4f}")

        print(
            f"\nRunning Vote (n_trials={args.n_trials}, prc_input={args.prc_input_space}, "
            f"baseline_input={args.baseline_input_space}, prc_similarity={args.prc_similarity}, "
            f"prc_sparse={prc_use_sparse}, tune_baselines={tune_baselines})..."
        )
        vote_results, vote_details = run_all_methods(
            args.vote_data,
            args.vote_k,
            args.seed,
            args.vote_dbscan_eps,
            args.vote_dbscan_min_samples,
            n_trials=args.n_trials,
            dataset_name="vote",
            use_standardized_for_prc=use_std_for_prc,
            baseline_input_space=args.baseline_input_space,
            prc_similarity=args.prc_similarity,
            prc_use_sparse=prc_use_sparse,
            tune_baselines=tune_baselines,
            prc_policy_template=prc_policy_template,
            prc_noise_last=noise_last,
            vote_missing_strategy=args.vote_missing_strategy,
        )
        print("Vote ARI results:")
        for k, v in vote_results.items():
            print(f"  {k:<25} ARI={v:.4f}")

        diagnostics_payload = {
            "mode": "experiment",
            "config": {
                "n_trials": args.n_trials,
                "vote_data": str(args.vote_data),
                "prc_input_space": args.prc_input_space,
                "baseline_input_space": args.baseline_input_space,
                "prc_similarity": args.prc_similarity,
                "prc_use_sparse": prc_use_sparse,
                "tune_baselines": tune_baselines,
                "prc_noise_last": noise_last,
                "prc_policy": {
                    "recurse_tilo": bool(args.prc_recurse_tilo),
                    "reverse_order_on_split": bool(args.reverse_order_on_split),
                    "return_recursive_order": bool(args.prc_return_recursive_order),
                    "refine_tilo": bool(args.prc_refine_tilo),
                },
                "vote_missing_strategy": args.vote_missing_strategy,
                "paper_profile": bool(args.paper_profile),
            },
            "iris": {
                "results": iris_results,
                "paper_reference": PAPER_IRIS_ARI,
                "paper_delta": calc_delta_to_paper(iris_results, PAPER_IRIS_ARI),
                "details": iris_details,
            },
            "vote": {
                "results": vote_results,
                "paper_reference": PAPER_VOTE_ARI,
                "paper_delta": calc_delta_to_paper(vote_results, PAPER_VOTE_ARI),
                "details": vote_details,
            },
            "paper_reference_note": PAPER_REFERENCE_NOTE,
        }

    if args.no_plot:
        print("\nSkipping figure generation (--no-plot).")
    else:
        print("\nGenerating figure...")
        plot_paper_figure(iris_results, vote_results, args.output)

    args.diagnostics.parent.mkdir(parents=True, exist_ok=True)
    args.diagnostics.write_text(json.dumps(diagnostics_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Saved diagnostics: {args.diagnostics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
