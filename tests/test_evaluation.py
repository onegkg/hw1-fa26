"""Tests for evaluation module."""

import pytest
from evaluation import accuracy, compute_metrics, f1_score, precision, recall


class TestAccuracy:
    """Tests for accuracy function."""

    def test_perfect_accuracy(self) -> None:
        predictions = [1, 0, 1, 0]
        labels = [1, 0, 1, 0]
        assert accuracy(predictions, labels) == 1.0

    def test_zero_accuracy(self) -> None:
        predictions = [1, 1, 1, 1]
        labels = [0, 0, 0, 0]
        assert accuracy(predictions, labels) == 0.0

    def test_partial_accuracy(self) -> None:
        predictions = [1, 0, 1, 0]
        labels = [1, 0, 0, 1]
        assert accuracy(predictions, labels) == 0.5

    def test_empty_predictions(self) -> None:
        assert accuracy([], []) == 0.0


class TestPrecision:
    """Tests for precision function."""

    def test_perfect_precision(self) -> None:
        predictions = [1, 1, 0, 0]
        labels = [1, 1, 0, 0]
        assert precision(predictions, labels) == 1.0

    def test_zero_precision(self) -> None:
        predictions = [1, 1, 1, 1]
        labels = [0, 0, 0, 0]
        assert precision(predictions, labels) == 0.0

    def test_partial_precision(self) -> None:
        # 2 true positives, 2 false positives
        predictions = [1, 1, 1, 1]
        labels = [1, 1, 0, 0]
        assert precision(predictions, labels) == 0.5

    def test_no_positive_predictions(self) -> None:
        predictions = [0, 0, 0, 0]
        labels = [1, 1, 0, 0]
        assert precision(predictions, labels) == 0.0


class TestRecall:
    """Tests for recall function."""

    def test_perfect_recall(self) -> None:
        predictions = [1, 1, 0, 0]
        labels = [1, 1, 0, 0]
        assert recall(predictions, labels) == 1.0

    def test_zero_recall(self) -> None:
        predictions = [0, 0, 0, 0]
        labels = [1, 1, 1, 1]
        assert recall(predictions, labels) == 0.0

    def test_partial_recall(self) -> None:
        # 1 true positive out of 2 actual positives
        predictions = [1, 0, 0, 0]
        labels = [1, 1, 0, 0]
        assert recall(predictions, labels) == 0.5

    def test_no_actual_positives(self) -> None:
        predictions = [1, 1, 1, 1]
        labels = [0, 0, 0, 0]
        assert recall(predictions, labels) == 0.0


class TestF1Score:
    """Tests for f1_score function."""

    def test_perfect_f1(self) -> None:
        predictions = [1, 1, 0, 0]
        labels = [1, 1, 0, 0]
        assert f1_score(predictions, labels) == 1.0

    def test_zero_f1(self) -> None:
        predictions = [0, 0, 0, 0]
        labels = [1, 1, 1, 1]
        assert f1_score(predictions, labels) == 0.0

    def test_f1_calculation(self) -> None:
        # precision = 2/3, recall = 2/2 = 1
        # f1 = 2 * (2/3 * 1) / (2/3 + 1) = 4/3 / 5/3 = 4/5 = 0.8
        predictions = [1, 1, 1, 0]
        labels = [1, 1, 0, 0]
        assert f1_score(predictions, labels) == pytest.approx(0.8)


class TestComputeMetrics:
    """Tests for compute_metrics function."""

    def test_compute_metrics_returns_all_metrics(self) -> None:
        predictions = [1, 0]
        labels = [1, 0]

        results = compute_metrics(predictions, labels)

        assert "accuracy" in results
        assert "precision" in results
        assert "recall" in results
        assert "f1" in results

        assert results["accuracy"] == 1.0
        assert results["precision"] == 1.0
        assert results["recall"] == 1.0
        assert results["f1"] == 1.0
