# PRC 冒烟测试
# 本模块包含 PRC/TILO 纯 Python 实现的基础冒烟测试。
from __future__ import annotations

import unittest

import numpy as np

import prc
import pyprc
from pyprc.matrix import MatrixStorage
from pyprc.order import VirtualOrderObject
from pyprc.io import loadSparseGraph


class TestPyPRCSmoke(unittest.TestCase):
    def test_pinch_ratio_clustering_runs(self) -> None:
        a = np.array(
            [
                [0, 1, 1, 0, 1, 0],
                [1, 0, 0, 1, 0, 1],
                [1, 0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0, 1],
                [1, 0, 1, 0, 0, 0],
                [0, 1, 0, 1, 0, 0],
            ],
            dtype=float,
        )
        order = pyprc.OrderObject(6)
        labels = [0] * 6
        res = pyprc.pinchRatioClustering(a, order, labels, 2, pyprc.PrcPolicyStruct())
        self.assertEqual(len(labels), 6)
        self.assertTrue(all(isinstance(v, int) for v in labels))
        self.assertIsInstance(res, pyprc.PrcReturnStruct)

    def test_gauss_similarity_returns_square(self) -> None:
        x = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], dtype=float)
        w, sigma = pyprc.gaussSimMatrix(x, -1.0, pyprc.GaussSimAdjMode.GS_ADJ_ALL)
        self.assertEqual(w.shape, (3, 3))
        self.assertGreater(sigma, 0.0)

    def test_tilo_public_signature(self) -> None:
        a = np.array(
            [
                [0.0, 1.0, 0.0],
                [1.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
            ]
        )
        order = pyprc.OrderObject(3)
        counts = pyprc.TILO(a, order, pyprc.TiloPolicyStruct())
        self.assertIsInstance(counts, pyprc.PrcCountsStruct)

    def test_root_prc_import_compatibility(self) -> None:
        self.assertIs(prc.PrcPolicyStruct, pyprc.PrcPolicyStruct)
        self.assertTrue(hasattr(prc, "pinchRatioClustering"))

    def test_virtual_order_split_shares_storage(self) -> None:
        base = pyprc.OrderObject(data=[0, 1, 2, 3])
        view = VirtualOrderObject(base)
        _, right = view.split(1, reverse_b=True)
        self.assertEqual(base.Print(), "0 1 3 2")
        self.assertEqual(right.Print(), "3 2")

    def test_enum_values_accessible(self) -> None:
        """验证枚举值可直接访问"""
        self.assertEqual(pyprc.TagModeEnum.FRONT_TAGS, 1)
        self.assertEqual(pyprc.FileStructureEnum.POINT_DATA, 0)
        self.assertEqual(pyprc.PointSimilarityEnum.KNN_ADJ_SIM, 2)
        self.assertEqual(pyprc.PrcMetricEnum.PinchRatio, 0)

    def test_recursive_return_order_path_runs(self) -> None:
        a = np.array(
            [
                [0.0, 1.0, 1.0, 0.0],
                [1.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 1.0],
                [0.0, 1.0, 1.0, 0.0],
            ]
        )
        order = pyprc.OrderObject(4)
        labels = [0] * 4
        policy = pyprc.PrcPolicyStruct()
        policy.prcRecurseTILO = True
        policy.prcReturnRecursiveOrder = True
        res = pyprc.pinchRatioClustering(a, order, labels, 2, policy)
        self.assertIsInstance(res, pyprc.PrcReturnStruct)
        self.assertEqual(order.size(), 4)
        self.assertEqual(len(labels), 4)

    def test_sparse_loader_keeps_sparse_storage(self) -> None:
        sparse_graph, _ = loadSparseGraph("tests/d1.txt", 0)
        storage = MatrixStorage(sparse_graph)
        self.assertTrue(storage.isSparse())
        self.assertEqual(storage.nnz(), 16)


if __name__ == "__main__":
    unittest.main()
