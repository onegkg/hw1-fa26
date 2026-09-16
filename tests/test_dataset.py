"""Tests for dataset module."""

import tempfile
from pathlib import Path

import pytest

from dataset import (
    SentimentInstance,
    get_statistics,
    load_data,
    load_instances,
    tokenize,
)


class TestTokenize:
    """Tests for tokenize function."""

    def test_lowercase(self) -> None:
        result = tokenize("Hello World")
        assert result == ["hello", "world"]

    def test_split_whitespace(self) -> None:
        result = tokenize("hello   world")
        assert result == ["hello", "world"]

    def test_strip_whitespace(self) -> None:
        result = tokenize("  hello  world  ")
        assert result == ["hello", "world"]

    def test_empty_string(self) -> None:
        result = tokenize("")
        assert result == []

    def test_mixed_case_and_whitespace(self) -> None:
        result = tokenize("  HeLLo   WoRLD  ")
        assert result == ["hello", "world"]


class TestSentimentInstance:
    """Tests for SentimentInstance dataclass."""

    def test_creation(self) -> None:
        instance = SentimentInstance(tokens=["hello", "world"], label=1)
        assert instance.tokens == ["hello", "world"]
        assert instance.label == 1

    def test_negative_label(self) -> None:
        instance = SentimentInstance(tokens=["bad", "movie"], label=0)
        assert instance.label == 0


class TestLoadInstances:
    """Tests for load_instances function."""

    def test_load_from_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create pos and neg directories
            (tmpdir / "pos").mkdir()
            (tmpdir / "neg").mkdir()

            # Create sample files
            (tmpdir / "pos" / "1.txt").write_text("Great movie")
            (tmpdir / "neg" / "1.txt").write_text("Terrible film")

            instances = load_instances(tmpdir)

            assert len(instances) == 2
            labels = [inst.label for inst in instances]
            assert 1 in labels
            assert 0 in labels

    def test_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            # Only create pos directory
            (tmpdir / "pos").mkdir()
            (tmpdir / "pos" / "1.txt").write_text("Good movie")

            instances = load_instances(tmpdir)

            assert len(instances) == 1
            assert instances[0].label == 1


class TestLoadData:
    """Tests for load_data function."""

    def test_load_train_and_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create train and test directories
            for split in ["train", "test"]:
                for label in ["pos", "neg"]:
                    (tmpdir / split / label).mkdir(parents=True)
                    (tmpdir / split / label / "1.txt").write_text("sample text")

            train, test = load_data(tmpdir)

            assert len(train) == 2
            assert len(test) == 2


class TestGetStatistics:
    """Tests for get_statistics function."""

    def test_statistics_calculation(self) -> None:
        train = [
            SentimentInstance(tokens=["good"], label=1),
            SentimentInstance(tokens=["good"], label=1),
            SentimentInstance(tokens=["bad"], label=0),
        ]
        test = [
            SentimentInstance(tokens=["ok"], label=1),
        ]

        stats = get_statistics(train, test)

        assert stats["train_count"] == 3
        assert stats["test_count"] == 1
        assert stats["train_pos_count"] == 2
        assert stats["train_neg_count"] == 1
        assert stats["train_pos_ratio"] == pytest.approx(2 / 3)
        assert stats["train_neg_ratio"] == pytest.approx(1 / 3)

    def test_empty_train(self) -> None:
        train = []
        test = [SentimentInstance(tokens=["ok"], label=1)]

        stats = get_statistics(train, test)

        assert stats["train_count"] == 0
        assert stats["train_pos_ratio"] == 0.0
        assert stats["train_neg_ratio"] == 0.0
