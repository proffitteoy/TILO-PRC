from __future__ import annotations

import unittest

import numpy as np

import pyprc


class _ControlledBackend:
    def __init__(self) -> None:
        self.calls = 0

    def init_random_order(self, n: int) -> pyprc.OrderObject:
        return pyprc.OrderObject(data=list(range(n)))

    def run_pinch_ratio_clustering(
        self,
        matrix: pyprc.MatrixStorage,
        order: pyprc.OrderObject,
        num_partitions: int,
        policy: pyprc.PrcPolicyStruct,
    ) -> tuple[pyprc.PrcReturnStruct, np.ndarray]:
        self.calls += 1
        order.boundary().resize(1, 0.0)
        order.boundary().set_at(0, float(10 - self.calls))
        labels = np.full(matrix.rows(), self.calls, dtype=int)
        return pyprc.PrcReturnStruct(), labels


class _FailingBackend:
    def init_random_order(self, n: int) -> pyprc.OrderObject:
        return pyprc.OrderObject(data=list(range(n)))

    def run_pinch_ratio_clustering(
        self,
        matrix: pyprc.MatrixStorage,
        order: pyprc.OrderObject,
        num_partitions: int,
        policy: pyprc.PrcPolicyStruct,
    ) -> tuple[pyprc.PrcReturnStruct, np.ndarray]:
        raise RuntimeError("forced backend failure")


class TestPipelineInterfaces(unittest.TestCase):
    def test_graph_build_config_delegates_similarity_builder(self) -> None:
        points = np.array([[0.0], [1.0], [3.0]], dtype=float)
        matrix, meta = pyprc.build_similarity_matrix_from_points(
            points,
            pyprc.GraphBuildConfig(
                similarity="gauss",
                use_sparse=False,
                gauss_mode=pyprc.GaussSimAdjMode.GS_ADJ_ALL,
                gauss_sigma=2.0,
            ),
        )
        self.assertIsInstance(matrix, pyprc.MatrixStorage)
        self.assertEqual(matrix.rows(), 3)
        self.assertEqual(meta["similarity"], "gauss")
        self.assertIn("gauss_sigma_used", meta)

    def test_best_of_trials_respects_backend_contract(self) -> None:
        backend = _ControlledBackend()
        matrix = pyprc.MatrixStorage(np.eye(4, dtype=float))
        labels = pyprc.run_best_of_trials(
            matrix=matrix,
            num_partitions=2,
            policy_template=pyprc.PrcPolicyStruct(),
            metric=pyprc.PrcMetricEnum.PinchRatio,
            n_trials=3,
            seed_start=123,
            backend=backend,
        )
        self.assertEqual(backend.calls, 3)
        self.assertTrue(np.array_equal(labels, np.full(4, 3, dtype=int)))

    def test_pipeline_service_runs_with_injected_backend(self) -> None:
        backend = _ControlledBackend()
        service = pyprc.PrcPipelineService(backend=backend)
        matrix = pyprc.MatrixStorage(np.eye(5, dtype=float))
        labels = service.run_best_of_trials(
            matrix=matrix,
            num_partitions=2,
            policy_template=pyprc.PrcPolicyStruct(),
            metric=pyprc.PrcMetricEnum.PinchRatio,
            n_trials=2,
            seed_start=1,
        )
        self.assertEqual(backend.calls, 2)
        self.assertTrue(np.array_equal(labels, np.full(5, 2, dtype=int)))

    def test_pipeline_service_build_graph_from_config(self) -> None:
        service = pyprc.PrcPipelineService()
        points = np.array([[0.0], [1.0], [2.0]], dtype=float)
        matrix, meta = service.build_similarity_matrix_from_points(
            points,
            pyprc.GraphBuildConfig(similarity="knn", use_sparse=False, knn_k=1),
        )
        self.assertIsInstance(matrix, pyprc.MatrixStorage)
        self.assertEqual(matrix.rows(), 3)
        self.assertEqual(meta["similarity"], "knn")

    def test_run_from_candidate_orders_supports_fallback(self) -> None:
        matrix = pyprc.MatrixStorage(np.eye(3, dtype=float))
        fallback = np.array([7, 8, 9], dtype=int)
        result = pyprc.run_from_candidate_orders(
            matrix=matrix,
            num_partitions=2,
            policy_template=pyprc.PrcPolicyStruct(),
            candidate_orders=[pyprc.OrderObject(data=[0, 1, 2])],
            continue_on_error=True,
            fallback_labels=fallback,
            backend=_FailingBackend(),
        )
        self.assertTrue(np.array_equal(result, fallback))


if __name__ == "__main__":
    unittest.main()
