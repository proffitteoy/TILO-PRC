from __future__ import annotations

import argparse
import unittest

import numpy as np

import pyprc
from experiments import reproduce_paper_fig_ari as repro


class TestReproducePaperProtocol(unittest.TestCase):
    def test_apply_paper_profile_overrides_without_forcing_prc_flags(self) -> None:
        args = argparse.Namespace(
            prc_input_space="standardized",
            baseline_input_space="standardized",
            prc_similarity="knn",
            prc_dense=True,
            vote_missing_strategy="half",
            prc_recurse_tilo=True,
            reverse_order_on_split=True,
            prc_return_recursive_order=True,
            prc_refine_tilo=True,
        )
        repro.apply_paper_profile_overrides(args)
        self.assertEqual(args.prc_input_space, "raw")
        self.assertEqual(args.baseline_input_space, "raw")
        self.assertEqual(args.prc_similarity, "gauss")
        self.assertFalse(args.prc_dense)
        self.assertEqual(args.vote_missing_strategy, "drop_rows")
        self.assertTrue(args.prc_recurse_tilo)
        self.assertTrue(args.reverse_order_on_split)
        self.assertTrue(args.prc_return_recursive_order)
        self.assertTrue(args.prc_refine_tilo)

    def test_resolve_seeded_label_permutations_priority(self) -> None:
        self.assertFalse(
            repro.resolve_seeded_label_permutations(
                argparse.Namespace(
                    label_permutations_for_seeded_baselines=False,
                    no_label_permutations_for_seeded_baselines=False,
                )
            )
        )
        self.assertTrue(
            repro.resolve_seeded_label_permutations(
                argparse.Namespace(
                    label_permutations_for_seeded_baselines=True,
                    no_label_permutations_for_seeded_baselines=False,
                )
            )
        )
        self.assertFalse(
            repro.resolve_seeded_label_permutations(
                argparse.Namespace(
                    label_permutations_for_seeded_baselines=True,
                    no_label_permutations_for_seeded_baselines=True,
                )
            )
        )

    def test_best_of_trials_seed_protocol_matches_single_srand_sequence(self) -> None:
        a = np.array(
            [
                [0.0, 1.0, 1.0, 0.0, 1.0, 0.0],
                [1.0, 0.0, 0.0, 1.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
                [0.0, 1.0, 1.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 1.0, 0.0, 0.0],
            ],
            dtype=float,
        )
        matrix = pyprc.MatrixStorage(a)
        policy_template = pyprc.PrcPolicyStruct(metric=pyprc.PrcMetricEnum.PinchRatio)
        n_trials = 4
        seed_start = 42

        from_helper = repro._run_tilo_variant_best_of_trials(
            matrix=matrix,
            num_partitions=2,
            policy_template=policy_template,
            metric=pyprc.PrcMetricEnum.PinchRatio,
            n_trials=n_trials,
            seed_start=seed_start,
        )

        policy = repro.clone_prc_policy(policy_template, metric=pyprc.PrcMetricEnum.PinchRatio)
        pyprc._GLOBAL_C_RAND.srand(seed_start)
        best_labels = None
        best_counts = None
        best_boundary = []
        for _ in range(n_trials):
            order = pyprc.initOrder_random(matrix.rows())
            counts, labels = pyprc.pinchRatioClustering_storage(matrix, order, 2, policy)
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

        self.assertIsNotNone(best_labels)
        self.assertTrue(np.array_equal(from_helper, best_labels))


if __name__ == "__main__":
    unittest.main()

