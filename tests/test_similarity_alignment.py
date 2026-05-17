from __future__ import annotations

import unittest

import numpy as np

import pyprc


class TestSimilarityAlignment(unittest.TestCase):
    def test_knn_mode_one_half_matches_half_symmetrized_binary_knn(self) -> None:
        # Distances are strictly ordered to avoid tie-breaking ambiguity.
        points = np.array([[0.0], [1.0], [3.0], [8.0]], dtype=float)
        k = 1
        directed = np.zeros((points.shape[0], points.shape[0]), dtype=float)
        for i in range(points.shape[0]):
            dist2 = np.sum((points - points[i]) ** 2, axis=1)
            nn = np.argsort(dist2)[: k + 1]
            for j in nn:
                if int(j) == i:
                    continue
                directed[i, int(j)] = 1.0
        expected = 0.5 * (directed + directed.T)

        dense, _ = pyprc.knnSimMatrix(
            points,
            k,
            pyprc.KNNAdjMode.KNN_BOTH_EITHER_ONE_ONEHALF,
            sigma=-1.0,
        )
        self.assertTrue(np.allclose(dense, expected))

        sparse, _ = pyprc.knnSimSparseMatrix(
            points,
            k,
            pyprc.KNNAdjMode.KNN_BOTH_EITHER_ONE_ONEHALF,
            sigma=-1.0,
        )
        self.assertTrue(np.allclose(sparse.to_dense(), expected))

    def test_gauss_dense_mode_all_keeps_full_matrix(self) -> None:
        points = np.array([[0.0], [1.0], [3.0]], dtype=float)
        sigma = 2.0
        dense, _ = pyprc.gaussSimMatrix(
            points,
            sigma=sigma,
            mode=pyprc.GaussSimAdjMode.GS_ADJ_ALL,
            eps=1.0,  # mode=ALL should ignore threshold
        )
        expected = np.zeros_like(dense)
        gamma = -1.0 / (2.0 * sigma * sigma)
        for i in range(points.shape[0]):
            for j in range(points.shape[0]):
                if i == j:
                    expected[i, j] = 0.0
                else:
                    expected[i, j] = np.exp(float(np.sum((points[i] - points[j]) ** 2)) * gamma)
        self.assertTrue(np.allclose(dense, expected))

    def test_gauss_threshold_modes_match_dense_and_sparse(self) -> None:
        points = np.array([[0.0], [1.0], [4.0]], dtype=float)
        sigma = 1.0
        threshold = 0.2
        dense, _ = pyprc.gaussSimMatrix(
            points,
            sigma=sigma,
            mode=pyprc.GaussSimAdjMode.GS_ADJ_THRESHOLD,
            eps=threshold,
        )
        sparse, _ = pyprc.gaussSimSparseMatrix(
            points,
            sigma=sigma,
            mode=pyprc.GaussSimAdjMode.GS_ADJ_THRESHOLD,
            eps=threshold,
        )
        self.assertTrue(np.allclose(dense, sparse.to_dense()))


if __name__ == "__main__":
    unittest.main()

