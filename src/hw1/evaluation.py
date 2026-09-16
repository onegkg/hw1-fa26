"""Evaluation metrics for sentiment analysis."""

import json
from pathlib import Path

import click


def accuracy(predictions, labels):
    """Compute accuracy.

    Args:
        predictions: List of predicted labels (1 or 0).
        labels: List of true labels (1 or 0).

    Returns:
        Accuracy score between 0 and 1.
    """
    if len(predictions) == 0:
        return 0.0

    correct = 0
    for pred, true in zip(predictions, labels, strict=True):
        if pred == true:
            correct = correct + 1

    return correct / len(predictions)


def precision(predictions, labels, positive_label=1):
    """Compute precision for the positive class.

    Args:
        predictions: List of predicted labels (1 or 0).
        labels: List of true labels (1 or 0).
        positive_label: The label considered as positive (default: 1).

    Returns:
        Precision score between 0 and 1.
    """
    true_positives = 0
    for pred, true in zip(predictions, labels, strict=True):
        if pred == positive_label and true == positive_label:
            true_positives = true_positives + 1

    predicted_positives = 0
    for pred in predictions:
        if pred == positive_label:
            predicted_positives = predicted_positives + 1

    if predicted_positives == 0:
        return 0.0
    return true_positives / predicted_positives


def recall(predictions, labels, positive_label=1):
    """Compute recall for the positive class.

    Args:
        predictions: List of predicted labels (1 or 0).
        labels: List of true labels (1 or 0).
        positive_label: The label considered as positive (default: 1).

    Returns:
        Recall score between 0 and 1.
    """
    true_positives = 0
    for pred, true in zip(predictions, labels, strict=True):
        if pred == positive_label and true == positive_label:
            true_positives = true_positives + 1

    actual_positives = 0
    for true in labels:
        if true == positive_label:
            actual_positives = actual_positives + 1

    if actual_positives == 0:
        return 0.0
    return true_positives / actual_positives


def f1_score(predictions, labels, positive_label=1):
    """Compute F1 score for the positive class.

    Args:
        predictions: List of predicted labels (1 or 0).
        labels: List of true labels (1 or 0).
        positive_label: The label considered as positive (default: 1).

    Returns:
        F1 score between 0 and 1.
    """
    p = precision(predictions, labels, positive_label)
    r = recall(predictions, labels, positive_label)

    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def compute_metrics(predictions, labels):
    """Compute all evaluation metrics.

    Args:
        predictions: List of predicted labels (1 or 0).
        labels: List of true labels (1 or 0).

    Returns:
        Dictionary containing accuracy, precision, recall, and f1 scores.
    """
    return {
        "accuracy": accuracy(predictions, labels),
        "precision": precision(predictions, labels),
        "recall": recall(predictions, labels),
        "f1": f1_score(predictions, labels),
    }


@click.command()
@click.argument("input_path", type=str)
@click.option("--output", "-o", default="build/", help="Output directory for metrics JSON")
@click.option("--run-tag", default="default", help="Tag for this pipeline run (creates subdirectory)")
@click.option("--schema-version", type=click.Choice(["1", "2"]), default="1", help="Output schema version")
def evaluate(input_path, output, run_tag, schema_version):
    """Evaluate predictions and compute metrics.

    INPUT_PATH: Path to predictions JSON file from rule_based.
    """
    schema_ver = int(schema_version)

    # Output goes to: <output>/<run_tag>/
    output_dir = Path(output) / run_tag
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo("Loading predictions from %s..." % input_path)
    click.echo("Run tag: %s, Schema version: %s" % (run_tag, schema_ver))
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    results = {}
    for split in ["train", "test"]:
        if split not in data:
            continue

        predictions = []
        for item in data[split]:
            predictions.append(item["pred"])

        labels = []
        for item in data[split]:
            labels.append(item["label"])

        metrics = compute_metrics(predictions, labels)

        # Report metrics as percentages for readability
        for name in metrics:
            metrics[name] = metrics[name] * 100

        # Schema v2 adds support counts
        if schema_ver == 2:
            pos_count = 0
            for label in labels:
                if label == 1:
                    pos_count = pos_count + 1

            neg_count = 0
            for label in labels:
                if label == 0:
                    neg_count = neg_count + 1

            metrics["support"] = {"positive": pos_count, "negative": neg_count}

        results[split] = metrics
        click.echo("%s metrics: accuracy=%.4f, precision=%.4f, recall=%.4f, f1=%.4f" % (
            split.capitalize(), metrics['accuracy'], metrics['precision'], metrics['recall'], metrics['f1']))

    # Save metrics to JSON
    metrics_path = output_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    click.echo("Saved metrics to %s" % metrics_path)


# CLI entry point: python -m hw1.evaluation --help
if __name__ == "__main__":
    evaluate()
