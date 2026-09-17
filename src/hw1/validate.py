"""Artifact validation module for pipeline contract enforcement.

This module validates that pipeline artifacts conform to the expected schema.
Students must fix linting and type errors in this file.
"""

import json
import sys
from pathlib import Path
from typing import Any, Literal

REQUIRED_METRICS = ["accuracy", "precision", "recall", "f1"]
VALID_LABELS = [0, 1]
SCHEMA_VERSIONS = [1, 2]


# data collection with [str] key dict[str, Any]
def validate_instances(
    data: dict[str, Any], schema_version: Literal[1, 2] = 1
) -> tuple[bool, list[str]]:
    """Validate instances.json artifact.

    Args:
        data: Parsed JSON data from instances.json
        schema_version: Schema version to validate against (1 or 2)

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Schema v2 requires metadata block
    if schema_version == 2:
        if "metadata" not in data:
            errors.append("Schema v2 requires 'metadata' field")
        elif not isinstance(data["metadata"], dict):
            errors.append("'metadata' must be a dictionary")
        elif data["metadata"].get("schema_version") != 2:
            errors.append("metadata.schema_version must be 2 for schema v2")

    # Check required top-level keys
    for split in ["train", "test"]:
        if split not in data:
            errors.append(f"Missing required key: {split}")
            continue

        instances = data[split]
        if not isinstance(instances, list):
            errors.append(f"{split} must be a list")
            continue

        for i, inst in enumerate(instances):
            # Check required instance fields
            if "tokens" not in inst:
                errors.append(f"{split}[{i}]: missing 'tokens' field")
            elif not isinstance(inst["tokens"], list):
                errors.append(f"{split}[{i}]: 'tokens' must be a list")

            if "label" not in inst:
                errors.append(f"{split}[{i}]: missing 'label' field" % (split, i))
            elif inst["label"] not in VALID_LABELS:
                errors.append(f"{split}[{i}]: 'label' must be 0 or 1, got %s")

    if len(errors) == 0:
        return True, errors
    return False, errors


def validate_predictions(
    data: dict[str, Any],
    schema_version: Literal[1, 2] = 1,
    instances_data: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    """Validate predictions.json artifact.

    Predictions must have the same structure as instances but with 'pred' field populated:
    one prediction per instance, in the same order. Schema v2 also requires 'confidence'
    field per instance.

    If instances_data (parsed instances.json) is given, each prediction is also checked
    against the instance it was made for.
    """
    errors = []

    for split in ["train", "test"]:
        if split not in data:
            errors.append(f"Missing required key: {split}")
            continue

        instances = data[split]
        if not isinstance(instances, list):
            errors.append(f"{split} must be a list")
            continue

        for i, inst in enumerate(instances):
            if "pred" not in inst:
                errors.append(f"{split}[{i}]: missing 'pred' field")
            elif inst["pred"] not in VALID_LABELS:
                errors.append(f"{split}[{i}]: 'pred' must be 0 or 1, got {inst['pred']}")

            if "label" not in inst:
                errors.append(f"{split}[{i}]: missing 'label' field")
            elif inst["label"] not in VALID_LABELS:
                errors.append(f"{split}[{i}]: 'label' must be 0 or 1")

            # Schema v2 requires confidence scores
            if schema_version == 2:
                if "confidence" not in inst:
                    errors.append(f"{split}[{i}]: schema v2 requires 'confidence' field")
                elif not isinstance(inst["confidence"], (int, float)):
                    errors.append(f"{split}[{i}]: 'confidence' must be a number")
                elif not (0 <= inst["confidence"] <= 1):
                    errors.append(f"{split}[{i}]: 'confidence' must be between 0 and 1")

        # Each prediction must belong to the instance at the same position
        if instances_data is not None and split in instances_data:
            for i, (source, inst) in enumerate(zip(instances_data[split], instances)):
                if source.get("tokens") != inst.get("tokens"):
                    errors.append(f"{split}[{i}]: tokens don't match instances.json")
                elif source.get("label") != inst.get("label"):
                    errors.append(f"{split}[{i}]: label doesn't match instances.json")

    if len(errors) == 0:
        return (True, errors)
    return (False, errors)


def validate_metrics(
    data: dict[str, Any], schema_version: Literal[1, 2] = 1
) -> tuple[bool, list[str]]:
    """Validate metrics.json artifact.

    Metrics must contain accuracy, precision, recall, and f1 for each split,
    with values between 0 and 1. Schema v2 also requires 'support' field.
    """
    errors = []

    for split in ["train", "test"]:
        if split not in data:
            errors.append(f"Missing required key: {split}")
            continue

        metrics = data[split]
        if not isinstance(metrics, dict):
            errors.append(f"{split} must be a dictionary")
            continue

        for metric_name in REQUIRED_METRICS:
            if metric_name not in metrics:
                errors.append(f"{split}: missing required metric '{metric_name}'")
            else:
                value = metrics[metric_name]
                if not isinstance(value, (int, float)):
                    errors.append(f"{split}.{metric_name}: must be a number")
                elif not (0 <= value <= 1):
                    errors.append(f"{split}.{metric_name}: must be between 0 and 1, got {value}")

        # Schema v2 requires support counts
        if schema_version == 2:
            if "support" not in metrics:
                errors.append(f"{split}: schema v2 requires 'support' field")
            elif not isinstance(metrics["support"], dict):
                errors.append(f"{split}.support: must be a dictionary")
            else:
                support = metrics["support"]
                for key in ["positive", "negative"]:
                    if key not in support:
                        errors.append(f"{split}.support: missing '{key}' count")
                    elif not isinstance(support[key], int):
                        errors.append(f"{split}.support.{key}: must be an integer")

    if len(errors) == 0:
        return True, errors
    return False, errors


def validate_artifact(
    artifact_path: str | Path,
    artifact_type: Literal["instances", "predictions", "metrics"],
    schema_version: Literal[1, 2] = 1,
    instances_path: str | Path | None = None,
) -> bool:
    """Validate a pipeline artifact file.

    Args:
        artifact_path: Path to the artifact JSON file
        artifact_type: One of 'instances', 'predictions', 'metrics'
        schema_version: Schema version to validate against
        instances_path: Optional path to instances.json; predictions are checked against it

    Returns:
        True if valid, False otherwise. Prints errors to stderr.
    """
    path = Path(artifact_path)

    if not path.exists():
        print(f"Error: {artifact_path} does not exist", file=sys.stderr)
        return False

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: {artifact_path} is not valid JSON: {e}", file=sys.stderr)
        return False

    if artifact_type == "instances":
        is_valid, errors = validate_instances(data, schema_version)
    elif artifact_type == "predictions":
        instances_data = None
        if instances_path is not None:
            with open(instances_path) as f:
                instances_data = json.load(f)
        is_valid, errors = validate_predictions(data, schema_version, instances_data)
    elif artifact_type == "metrics":
        is_valid, errors = validate_metrics(data, schema_version)
    else:
        print(f"Error: Unknown artifact type '{artifact_type}'", file=sys.stderr)
        return False

    if not is_valid:
        print(f"Validation failed for {artifact_path}:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False
    print(f"Validation passed: {artifact_path}")
    return True


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate pipeline artifacts")
    parser.add_argument("artifact_path", help="Path to artifact JSON file")
    parser.add_argument(
        "--type",
        "-t",
        required=True,
        choices=["instances", "predictions", "metrics"],
        help="Artifact type to validate",
    )
    parser.add_argument(
        "--schema-version", type=int, default=1, choices=SCHEMA_VERSIONS, help="Schema version"
    )
    parser.add_argument("--instances", help="Path to instances.json (predictions only)")

    args = parser.parse_args()
    success = validate_artifact(args.artifact_path, args.type, args.schema_version, args.instances)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
