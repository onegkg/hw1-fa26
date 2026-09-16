"""Data preprocessing module for sentiment analysis."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import click


@dataclass
class SentimentInstance:
    """Represents a preprocessed sentiment instance."""
    tokens: List[str]
    label: int  # 1 for positive, 0 for negative
    pred: Optional[int] = field(default=None)  # Prediction, assigned after classification


def tokenize(text):
    """Tokenize text by lowercasing, splitting, and stripping whitespace.

    Args:
        text: Raw text string to tokenize.

    Returns:
        List of lowercase tokens with whitespace stripped.
    """
    tokens = []
    for token in text.lower().split():
        stripped = token.strip()
        if stripped:
            tokens.append(stripped)
    return tokens


def load_instances(data_dir):
    """Load sentiment instances from a directory containing pos/ and neg/ subdirs.

    Args:
        data_dir: Path to directory containing pos/ and neg/ subdirectories.

    Returns:
        List of SentimentInstance objects.
    """
    data_dir = Path(data_dir)
    instances = []

    label_map = {"pos": 1, "neg": 0}
    for label_name, label_value in label_map.items():
        label_dir = data_dir / label_name
        if label_dir.exists():
            for txt_file in label_dir.glob("*.txt"):
                text = txt_file.read_text(encoding="utf-8")
                tokens = tokenize(text)
                instances.append(SentimentInstance(tokens=tokens, label=label_value))

    return instances


def load_data(base_path):
    """Load train and test datasets.

    Args:
        base_path: Path to data directory containing train/ and test/ subdirs.

    Returns:
        Tuple of (train_instances, test_instances).
    """
    base_path = Path(base_path)
    train_instances = load_instances(base_path / "train")
    test_instances = load_instances(base_path / "test")
    return train_instances, test_instances


def get_statistics(train_instances, test_instances):
    """Compute dataset statistics.

    Args:
        train_instances: List of training instances.
        test_instances: List of test instances.

    Returns:
        Dictionary containing dataset statistics.
    """
    train_pos = 0
    for inst in train_instances:
        if inst.label == 1:
            train_pos = train_pos + 1

    train_neg = 0
    for inst in train_instances:
        if inst.label == 0:
            train_neg = train_neg + 1

    train_total = len(train_instances)

    if train_total > 0:
        pos_ratio = train_pos / train_total
        neg_ratio = train_neg / train_total
    else:
        pos_ratio = 0.0
        neg_ratio = 0.0

    return {
        "train_count": train_total,
        "test_count": len(test_instances),
        "train_pos_count": train_pos,
        "train_neg_count": train_neg,
        "train_pos_ratio": pos_ratio,
        "train_neg_ratio": neg_ratio,
    }


@click.command()
@click.argument("data_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="build/", help="Output directory for JSON files")
@click.option("--run-tag", default="default", help="Tag for this pipeline run (creates subdirectory)")
@click.option("--schema-version", type=click.Choice(["1", "2"]), default="1", help="Output schema version")
def preprocess(data_path, output, run_tag, schema_version):
    """Load and preprocess the dataset, save instances and statistics as JSON.

    DATA_PATH: Path to data directory containing train/ and test/ subdirs.
    """
    schema_ver = int(schema_version)

    # Output goes to: <output>/<run_tag>/
    output_dir = Path(output) / run_tag
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo("Loading data from %s..." % data_path)
    click.echo("Run tag: %s, Schema version: %s" % (run_tag, schema_ver))
    train_instances, test_instances = load_data(data_path)
    stats = get_statistics(train_instances, test_instances)

    train_data = []
    for inst in train_instances:
        train_data.append(asdict(inst))

    test_data = []
    for inst in test_instances:
        test_data.append(asdict(inst))

    instances_data = {
        "train": train_data,
        "test": test_data,
    }

    # Schema v2 adds metadata block
    if schema_ver == 2:
        instances_data["metadata"] = {"schema_version": 2}

    # Save instances to JSON
    instances_path = output_dir / "instances.json"
    with open(instances_path, "w", encoding="utf-8") as f:
        json.dump(instances_data, f, indent=2)
    click.echo("Saved instances to %s" % instances_path)

    # Save statistics to JSON
    stats_path = output_dir / "statistics.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    click.echo("Saved statistics to %s" % stats_path)

    click.echo("Train: %s instances (pos: %s, neg: %s)" % (stats['train_count'], stats['train_pos_count'], stats['train_neg_count']))
    click.echo("Test: %s instances" % stats['test_count'])
    click.echo("Label ratio in train - pos: %.2f%%, neg: %.2f%%" % (stats['train_pos_ratio'] * 100, stats['train_neg_ratio'] * 100))


# CLI entry point: python -m hw1.dataset --help
if __name__ == "__main__":
    preprocess()
