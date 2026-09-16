"""Classifier models for sentiment analysis."""

import json
import math
from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set

import click
from textblob import TextBlob

from hw1.dataset import SentimentInstance


class Classifier(ABC):
    """Abstract base class for sentiment classifiers."""

    @abstractmethod
    def predict(self, instance):
        """Predict the sentiment label for an instance.

        Args:
            instance: A preprocessed SentimentInstance.

        Returns:
            Predicted label: 1 for positive, 0 for negative.
        """
        pass


class RuleBasedClassifier(Classifier):
    """Rule-based classifier using TextBlob sentiment analysis."""

    def predict(self, instance):
        """Predict sentiment based on TextBlob polarity score.

        Args:
            instance: A preprocessed SentimentInstance.

        Returns:
            Predicted label: 1 for positive, 0 for negative.
        """
        text = " ".join(instance.tokens)
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        return polarity > 0


class NaiveBayesClassifier(Classifier):
    """Naive Bayes classifier using Maximum Likelihood Estimation."""

    def __init__(self, smoothing=1.0):
        """Initialize the classifier.

        Args:
            smoothing: Laplace smoothing parameter (default: 1.0).
        """
        self.smoothing = smoothing
        self.class_priors = {}
        self.word_counts = {}
        self.class_totals = {}
        self.vocabulary = set()

    def fit(self, instances):
        """Train the classifier using MLE.

        Args:
            instances: List of training SentimentInstance objects.
        """
        class_counts = Counter()
        self.word_counts = {1: Counter(), 0: Counter()}
        self.vocabulary = set()

        for instance in instances:
            label = instance.label
            class_counts[label] += 1
            self.word_counts[label].update(instance.tokens)
            self.vocabulary.update(instance.tokens)

        total_instances = len(instances)

        self.class_priors = {}
        for label, count in class_counts.items():
            self.class_priors[label] = count / total_instances

        self.class_totals = {}
        for label, counts in self.word_counts.items():
            self.class_totals[label] = sum(counts.values())

    def _log_likelihood(self, tokens, label):
        """Compute log likelihood of tokens given a class label.

        Args:
            tokens: List of tokens.
            label: Class label (1 or 0).

        Returns:
            Log likelihood value.
        """
        vocab_size = len(self.vocabulary)
        total = self.class_totals.get(label, 0)
        log_prob = 0.0

        for token in tokens:
            count = self.word_counts[label].get(token, 0)
            prob = (count + self.smoothing) / (total + self.smoothing * vocab_size)
            log_prob += math.log(prob)

        return log_prob

    def predict(self, instance):
        """Predict sentiment using Naive Bayes.

        Args:
            instance: A preprocessed SentimentInstance.

        Returns:
            Predicted label: 1 for positive, 0 for negative.
        """
        best_label = 1
        best_score = float("-inf")

        for label in [1, 0]:
            if label not in self.class_priors:
                continue

            log_prior = math.log(self.class_priors[label])
            log_likelihood = self._log_likelihood(instance.tokens, label)
            score = log_prior + log_likelihood

            if score > best_score:
                best_score = score
                best_label = label

        return best_label


@click.command()
@click.option("--file", "-f", "file_path", type=str, required=True, help="Path to instances JSON file from preprocess")
@click.option("--output", "-o", default="build/", help="Output directory for predictions JSON")
@click.option("--run-tag", default="default", help="Tag for this pipeline run (creates subdirectory)")
@click.option("--schema-version", type=click.Choice(["1", "2"]), default="1", help="Output schema version")
def rule_based(file_path, output, run_tag, schema_version):
    """Predict sentiment using rule-based classifier.

    Processes a JSON file from preprocess and outputs predictions.
    """
    schema_ver = int(schema_version)

    # Output goes to: <output>/<run_tag>/
    output_dir = Path(output) / run_tag
    output_dir.mkdir(parents=True, exist_ok=True)

    input_file = Path(file_path)
    if not input_file.exists():
        raise click.UsageError("File not found: %s" % file_path)
    if input_file.suffix != ".json":
        raise click.UsageError("File must be a JSON file: %s" % file_path)

    click.echo("Loading instances from %s..." % file_path)
    click.echo("Run tag: %s, Schema version: %s" % (run_tag, schema_ver))
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    classifier = RuleBasedClassifier()

    results = {}
    for split in ["train", "test"]:
        if split not in data:
            continue

        instances = []
        for item in data[split]:
            inst = SentimentInstance(
                tokens=item["tokens"],
                label=item["label"],
                pred=item.get("pred"),
            )
            instances.append(inst)

        click.echo("Making predictions for %s %s instances..." % (len(instances), split))

        split_results = []
        for inst in instances:
            inst.pred = classifier.predict(inst)

            # Get confidence score for schema v2
            text = " ".join(inst.tokens)
            blob = TextBlob(text)
            confidence = abs(blob.sentiment.polarity)  # 0 to 1

            result = {
                "tokens": inst.tokens,
                "label": inst.label,
                "pred": inst.pred,
            }

            # Schema v2 adds confidence scores
            if schema_ver == 2:
                result["confidence"] = round(confidence, 4)

            split_results.append(result)

        results[split] = split_results

    # Save predictions to JSON
    predictions_path = output_dir / "predictions.json"
    with open(predictions_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    click.echo("Saved predictions to %s" % predictions_path)


# CLI entry point: python -m hw1.models --help
if __name__ == "__main__":
    rule_based()
