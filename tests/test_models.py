"""Tests for models module."""

import pytest

from dataset import SentimentInstance
from models import NaiveBayesClassifier, RuleBasedClassifier


class TestRuleBasedClassifier:
    """Tests for RuleBasedClassifier."""

    def test_positive_prediction(self) -> None:
        classifier = RuleBasedClassifier()
        instance = SentimentInstance(tokens=["great", "amazing", "wonderful"], label=1)
        prediction = classifier.predict(instance)
        assert prediction == 1

    def test_negative_prediction(self) -> None:
        classifier = RuleBasedClassifier()
        instance = SentimentInstance(tokens=["terrible", "awful", "horrible"], label=0)
        prediction = classifier.predict(instance)
        assert prediction == 0

    def test_neutral_defaults_to_negative(self) -> None:
        classifier = RuleBasedClassifier()
        instance = SentimentInstance(tokens=["the", "a", "is"], label=1)
        prediction = classifier.predict(instance)
        # TextBlob returns 0 polarity for neutral text, which maps to 0
        assert prediction == 0


class TestNaiveBayesClassifier:
    """Tests for NaiveBayesClassifier."""

    def test_fit_and_predict(self) -> None:
        classifier = NaiveBayesClassifier()

        train_data = [
            SentimentInstance(tokens=["good", "great", "excellent"], label=1),
            SentimentInstance(tokens=["good", "nice", "wonderful"], label=1),
            SentimentInstance(tokens=["bad", "terrible", "awful"], label=0),
            SentimentInstance(tokens=["bad", "poor", "horrible"], label=0),
        ]

        classifier.fit(train_data)

        # Test positive instance
        pos_instance = SentimentInstance(tokens=["good", "great"], label=1)
        assert classifier.predict(pos_instance) == 1

        # Test negative instance
        neg_instance = SentimentInstance(tokens=["bad", "terrible"], label=0)
        assert classifier.predict(neg_instance) == 0

    def test_class_priors(self) -> None:
        classifier = NaiveBayesClassifier()

        train_data = [
            SentimentInstance(tokens=["a"], label=1),
            SentimentInstance(tokens=["b"], label=1),
            SentimentInstance(tokens=["c"], label=0),
        ]

        classifier.fit(train_data)

        assert classifier.class_priors[1] == pytest.approx(2 / 3)
        assert classifier.class_priors[0] == pytest.approx(1 / 3)

    def test_vocabulary(self) -> None:
        classifier = NaiveBayesClassifier()

        train_data = [
            SentimentInstance(tokens=["hello", "world"], label=1),
            SentimentInstance(tokens=["goodbye", "world"], label=0),
        ]

        classifier.fit(train_data)

        assert classifier.vocabulary == {"hello", "world", "goodbye"}

    def test_smoothing(self) -> None:
        classifier = NaiveBayesClassifier(smoothing=1.0)

        train_data = [
            SentimentInstance(tokens=["good"], label=1),
            SentimentInstance(tokens=["bad"], label=0),
        ]

        classifier.fit(train_data)

        # Test with unseen word - should not raise error due to smoothing
        instance = SentimentInstance(tokens=["unknown"], label=1)
        prediction = classifier.predict(instance)
        assert prediction in [0, 1]
