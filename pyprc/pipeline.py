"""Service-layer orchestration helpers for PRC workflows.

This module sits between algorithm primitives and higher-level callers
(CLI scripts, experiments, notebooks). It keeps policy cloning, graph
construction, best-of-trials selection, and order-source strategies in
one reusable place.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from itertools import permutations
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple

import numpy as np

from .algorithm import cless, initOrder_random, pinchRatioClustering_storage
from .enums import GaussSimAdjMode, KNNAdjMode, PRCError, PrcMetricEnum
from .matrix import MatrixStorage
from .order import OrderObject
from .rng import _GLOBAL_C_RAND
from .similarity import (
    gaussSimMatrix,
    gaussSimSparseMatrix,
    knnSimMatrix,
    knnSimSparseMatrix,
)
from .structs import PrcPolicyStruct, PrcReturnStruct, TiloPolicyStruct


class PrcExecutionBackend(Protocol):
    """Backend contract for PRC execution."""

    def init_random_order(self, n: int) -> OrderObject:
        """Return a new randomized order object of size n."""

    def run_pinch_ratio_clustering(
        self,
        matrix: MatrixStorage,
        order: OrderObject,
        num_partitions: int,
        policy: PrcPolicyStruct,
    ) -> Tuple[PrcReturnStruct, np.ndarray]:
        """Run PRC clustering and return counts + labels."""


class PythonPrcExecutionBackend:
    """Default backend using the local pure-Python implementation."""

    def init_random_order(self, n: int) -> OrderObject:
        return initOrder_random(n)

    def run_pinch_ratio_clustering(
        self,
        matrix: MatrixStorage,
        order: OrderObject,
        num_partitions: int,
        policy: PrcPolicyStruct,
    ) -> Tuple[PrcReturnStruct, np.ndarray]:
        return pinchRatioClustering_storage(matrix, order, num_partitions, policy)


DEFAULT_BACKEND: PrcExecutionBackend = PythonPrcExecutionBackend()


@dataclass(frozen=True)
class GraphBuildConfig:
    """Inputs for building a similarity graph from point data."""

    similarity: str = "gauss"
    use_sparse: bool = True
    knn_k: int = -1
    knn_mode: KNNAdjMode = KNNAdjMode.KNN_EITHER_ADJ_GAUSS
    knn_sigma: float = -1.0
    gauss_sigma: float = -1.0
    gauss_mode: GaussSimAdjMode = GaussSimAdjMode.GS_ADJ_THRESHOLD
    gauss_threshold: float = 1e-10


class PrcPipelineService:
    """Class-based PRC orchestration service.

    This class wraps previously function-based helpers into a cohesive
    service object while keeping the underlying algorithm code unchanged.
    """

    def __init__(self, backend: PrcExecutionBackend = DEFAULT_BACKEND) -> None:
        self.backend = backend

    def seed_global_prc_rng(self, seed: int) -> int:
        """Seed the global PRC RNG using C++-style semantics."""
        if int(seed) == 0:
            resolved = int(time.time())
        else:
            resolved = int(seed)
        _GLOBAL_C_RAND.srand(resolved)
        return resolved

    def clone_prc_policy(
        self,
        policy: PrcPolicyStruct,
        metric: Optional[PrcMetricEnum] = None,
        prc_recurse_tilo: Optional[bool] = None,
        reverse_order_on_split: Optional[bool] = None,
        prc_return_recursive_order: Optional[bool] = None,
        prc_refine_tilo: Optional[bool] = None,
        tilo_max_iterations: Optional[int] = None,
    ) -> PrcPolicyStruct:
        """Copy a policy template with selected field overrides."""
        return PrcPolicyStruct(
            tiloPolicy=TiloPolicyStruct(
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

    def build_similarity_matrix_from_points(
        self,
        points: np.ndarray,
        config: GraphBuildConfig,
    ) -> Tuple[MatrixStorage, Dict[str, Any]]:
        """Build MatrixStorage from points using a unified graph policy."""
        graph_params: Dict[str, Any] = {
            "similarity": config.similarity,
            "use_sparse": bool(config.use_sparse),
        }

        if config.similarity == "knn":
            if config.use_sparse:
                matrix_like, k_or_sigma = knnSimSparseMatrix(
                    points,
                    config.knn_k,
                    config.knn_mode,
                    config.knn_sigma,
                )
            else:
                matrix_like, k_or_sigma = knnSimMatrix(
                    points,
                    config.knn_k,
                    config.knn_mode,
                    config.knn_sigma,
                )
            graph_params.update(
                {
                    "knn_k_input": int(config.knn_k),
                    "knn_mode": str(config.knn_mode),
                    "knn_sigma_input": float(config.knn_sigma),
                    "knn_meta": float(k_or_sigma),
                }
            )
            return MatrixStorage(matrix_like), graph_params

        if config.similarity == "gauss":
            if config.use_sparse:
                matrix_like, sigma_used = gaussSimSparseMatrix(
                    points,
                    config.gauss_sigma,
                    config.gauss_mode,
                    config.gauss_threshold,
                )
            else:
                matrix_like, sigma_used = gaussSimMatrix(
                    points,
                    config.gauss_sigma,
                    config.gauss_mode,
                    config.gauss_threshold,
                )
            graph_params.update(
                {
                    "gauss_sigma_input": float(config.gauss_sigma),
                    "gauss_mode": str(config.gauss_mode),
                    "gauss_threshold": float(config.gauss_threshold),
                    "gauss_sigma_used": float(sigma_used),
                }
            )
            return MatrixStorage(matrix_like), graph_params

        raise PRCError(f"Unknown similarity type: {config.similarity!r}")

    def orders_from_label_blocks(
        self,
        labels: Sequence[int],
        n: int,
        noise_last: bool = True,
        try_permutations: bool = False,
        max_permutation_labels: int = 8,
    ) -> Iterable[OrderObject]:
        """Convert labels into initial-order candidates (grouped by label)."""
        if len(labels) != n:
            raise PRCError(f"Initial labels size mismatch: {len(labels)} vs {n}")

        buckets: Dict[int, List[int]] = {}
        for idx, lbl in enumerate(labels):
            buckets.setdefault(int(lbl), []).append(idx)

        def key_sort(key: int) -> Tuple[int, int]:
            if noise_last:
                return (1 if key == -1 else 0, key)
            return (0, key)

        keys = sorted(buckets.keys(), key=key_sort)
        if try_permutations and len(keys) <= int(max_permutation_labels):
            key_orders: Iterable[Tuple[int, ...]] = permutations(keys)
        else:
            key_orders = [tuple(keys)]

        for key_order in key_orders:
            order_vec: List[int] = []
            for key in key_order:
                order_vec.extend(buckets[key])
            yield OrderObject(data=order_vec)

    def run_best_of_trials(
        self,
        matrix: MatrixStorage,
        num_partitions: int,
        policy_template: PrcPolicyStruct,
        metric: PrcMetricEnum,
        n_trials: int,
        seed_start: int,
        backend: Optional[PrcExecutionBackend] = None,
    ) -> np.ndarray:
        """Run randomized PRC multiple times and keep best run by C++-style rule."""
        if n_trials <= 0:
            raise PRCError(f"n_trials must be > 0, got {n_trials}")

        exec_backend = backend or self.backend
        policy = self.clone_prc_policy(policy_template, metric=metric)
        best_labels: Optional[np.ndarray] = None
        best_counts: Optional[PrcReturnStruct] = None
        best_boundary: List[float] = []
        self.seed_global_prc_rng(seed_start)

        for _ in range(n_trials):
            order = exec_backend.init_random_order(matrix.rows())
            counts, labels = exec_backend.run_pinch_ratio_clustering(
                matrix=matrix,
                order=order,
                num_partitions=num_partitions,
                policy=policy,
            )
            boundary = sorted(order.boundary().data(), reverse=True)
            if best_labels is None:
                best_labels = labels.copy()
                best_counts = counts
                best_boundary = list(boundary)
                continue
            if cless(counts, best_counts, boundary, best_boundary):  # type: ignore[arg-type]
                best_labels = labels.copy()
                best_counts = counts
                best_boundary = list(boundary)

        if best_labels is None:
            raise PRCError("No labels produced by best-of-trials execution")
        return best_labels

    def run_from_candidate_orders(
        self,
        matrix: MatrixStorage,
        num_partitions: int,
        policy_template: PrcPolicyStruct,
        candidate_orders: Iterable[OrderObject],
        metric: PrcMetricEnum = PrcMetricEnum.PinchRatio,
        continue_on_error: bool = False,
        fallback_labels: Optional[np.ndarray] = None,
        backend: Optional[PrcExecutionBackend] = None,
    ) -> np.ndarray:
        """Evaluate candidate initial orders and keep the best PRC result."""
        exec_backend = backend or self.backend
        policy = self.clone_prc_policy(policy_template, metric=metric)
        best_labels: Optional[np.ndarray] = None
        best_counts: Optional[PrcReturnStruct] = None
        best_boundary: List[float] = []

        for order in candidate_orders:
            try:
                counts, labels = exec_backend.run_pinch_ratio_clustering(
                    matrix=matrix,
                    order=order,
                    num_partitions=num_partitions,
                    policy=policy,
                )
            except Exception:
                if continue_on_error:
                    continue
                raise
            boundary = sorted(order.boundary().data(), reverse=True)
            if best_labels is None:
                best_labels = labels.copy()
                best_counts = counts
                best_boundary = list(boundary)
                continue
            if cless(counts, best_counts, boundary, best_boundary):  # type: ignore[arg-type]
                best_labels = labels.copy()
                best_counts = counts
                best_boundary = list(boundary)

        if best_labels is None:
            if fallback_labels is not None:
                return np.asarray(fallback_labels, dtype=int).copy()
            raise PRCError("No candidate order produced labels")
        return best_labels


DEFAULT_PIPELINE: PrcPipelineService = PrcPipelineService()


def seed_global_prc_rng(seed: int) -> int:
    """Compatibility wrapper for class-based PRC pipeline service."""
    return DEFAULT_PIPELINE.seed_global_prc_rng(seed)


def clone_prc_policy(
    policy: PrcPolicyStruct,
    metric: Optional[PrcMetricEnum] = None,
    prc_recurse_tilo: Optional[bool] = None,
    reverse_order_on_split: Optional[bool] = None,
    prc_return_recursive_order: Optional[bool] = None,
    prc_refine_tilo: Optional[bool] = None,
    tilo_max_iterations: Optional[int] = None,
) -> PrcPolicyStruct:
    """Compatibility wrapper for class-based PRC pipeline service."""
    return DEFAULT_PIPELINE.clone_prc_policy(
        policy=policy,
        metric=metric,
        prc_recurse_tilo=prc_recurse_tilo,
        reverse_order_on_split=reverse_order_on_split,
        prc_return_recursive_order=prc_return_recursive_order,
        prc_refine_tilo=prc_refine_tilo,
        tilo_max_iterations=tilo_max_iterations,
    )


def build_similarity_matrix_from_points(
    points: np.ndarray,
    config: GraphBuildConfig,
) -> Tuple[MatrixStorage, Dict[str, Any]]:
    """Compatibility wrapper for class-based PRC pipeline service."""
    return DEFAULT_PIPELINE.build_similarity_matrix_from_points(points, config)


def run_best_of_trials(
    matrix: MatrixStorage,
    num_partitions: int,
    policy_template: PrcPolicyStruct,
    metric: PrcMetricEnum,
    n_trials: int,
    seed_start: int,
    backend: PrcExecutionBackend = DEFAULT_BACKEND,
) -> np.ndarray:
    """Compatibility wrapper for class-based PRC pipeline service."""
    return DEFAULT_PIPELINE.run_best_of_trials(
        matrix=matrix,
        num_partitions=num_partitions,
        policy_template=policy_template,
        metric=metric,
        n_trials=n_trials,
        seed_start=seed_start,
        backend=backend,
    )


def orders_from_label_blocks(
    labels: Sequence[int],
    n: int,
    noise_last: bool = True,
    try_permutations: bool = False,
    max_permutation_labels: int = 8,
) -> Iterable[OrderObject]:
    """Compatibility wrapper for class-based PRC pipeline service."""
    return DEFAULT_PIPELINE.orders_from_label_blocks(
        labels=labels,
        n=n,
        noise_last=noise_last,
        try_permutations=try_permutations,
        max_permutation_labels=max_permutation_labels,
    )


def run_from_candidate_orders(
    matrix: MatrixStorage,
    num_partitions: int,
    policy_template: PrcPolicyStruct,
    candidate_orders: Iterable[OrderObject],
    metric: PrcMetricEnum = PrcMetricEnum.PinchRatio,
    continue_on_error: bool = False,
    fallback_labels: Optional[np.ndarray] = None,
    backend: PrcExecutionBackend = DEFAULT_BACKEND,
) -> np.ndarray:
    """Compatibility wrapper for class-based PRC pipeline service."""
    return DEFAULT_PIPELINE.run_from_candidate_orders(
        matrix=matrix,
        num_partitions=num_partitions,
        policy_template=policy_template,
        candidate_orders=candidate_orders,
        metric=metric,
        continue_on_error=continue_on_error,
        fallback_labels=fallback_labels,
        backend=backend,
    )
