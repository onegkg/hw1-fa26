"""Artifact validation module for pipeline contract enforcement.

This module validates that pipeline artifacts conform to the expected schema.
Students must fix linting and type errors in this file.
"""

import json
import sys
from pathlib import Path

REQUIRED_METRICS = ["accuracy", "precision", "recall", "f1"]
VALID_LABELS = [0, 1]
SCHEMA_VERSIONS = [1, 2]


def validate_instances(data, schema_version=1):
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
            errors.append("Missing required key: %s" % split)
            continue

        instances = data[split]
        if not isinstance(instances, list):
            errors.append("%s must be a list" % split)
            continue

        for i, inst in enumerate(instances):
            # Check required instance fields
            if "tokens" not in inst:
                errors.append("%s[%s]: missing 'tokens' field" % (split, i))
            elif not isinstance(inst["tokens"], list):
                errors.append("%s[%s]: 'tokens' must be a list" % (split, i))

            if "label" not in inst:
                errors.append("%s[%s]: missing 'label' field" % (split, i))
            elif inst["label"] not in VALID_LABELS:
                errors.append("%s[%s]: 'label' must be 0 or 1, got %s" % (split, i, inst['label']))

    if len(errors) == 0:
        return True, errors
    return False, errors


def validate_predictions(data, schema_version=1, instances_data=None):
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
            errors.append("Missing required key: %s" % split)
            continue

        instances = data[split]
        if not isinstance(instances, list):
            errors.append("%s must be a list" % split)
            continue

        for i, inst in enumerate(instances):
            if "pred" not in inst:
                errors.append("%s[%s]: missing 'pred' field" % (split, i))
            elif inst["pred"] not in VALID_LABELS:
                errors.append("%s[%s]: 'pred' must be 0 or 1, got %s" % (split, i, inst['pred']))

            if "label" not in inst:
                errors.append("%s[%s]: missing 'label' field" % (split, i))
            elif inst["label"] not in VALID_LABELS:
                errors.append("%s[%s]: 'label' must be 0 or 1" % (split, i))

            # Schema v2 requires confidence scores
            if schema_version == 2:
                if "confidence" not in inst:
                    errors.append("%s[%s]: schema v2 requires 'confidence' field" % (split, i))
                elif not isinstance(inst["confidence"], (int, float)):
                    errors.append("%s[%s]: 'confidence' must be a number" % (split, i))
                elif not (0 <= inst["confidence"] <= 1):
                    errors.append("%s[%s]: 'confidence' must be between 0 and 1" % (split, i))

        # Each prediction must belong to the instance at the same position
        if instances_data is not None and split in instances_data:
            for i, (source, inst) in enumerate(zip(instances_data[split], instances)):
                if source.get("tokens") != inst.get("tokens"):
                    errors.append("%s[%s]: tokens don't match instances.json" % (split, i))
                elif source.get("label") != inst.get("label"):
                    errors.append("%s[%s]: label doesn't match instances.json" % (split, i))

    if len(errors) == 0:
        return (True, errors)
    return (False, errors)


def validate_metrics(data, schema_version=1):
    """Validate metrics.json artifact.

    Metrics must contain accuracy, precision, recall, and f1 for each split,
    with values between 0 and 1. Schema v2 also requires 'support' field.
    """
    errors = []

    for split in ["train", "test"]:
        if split not in data:
            errors.append("Missing required key: %s" % split)
            continue

        metrics = data[split]
        if not isinstance(metrics, dict):
            errors.append("%s must be a dictionary" % split)
            continue

        for metric_name in REQUIRED_METRICS:
            if metric_name not in metrics:
                errors.append("%s: missing required metric '%s'" % (split, metric_name))
            else:
                value = metrics[metric_name]
                if not isinstance(value, (int, float)):
                    errors.append("%s.%s: must be a number" % (split, metric_name))
                elif not (0 <= value <= 1):
                    errors.append("%s.%s: must be between 0 and 1, got %s" % (split, metric_name, value))

        # Schema v2 requires support counts
        if schema_version == 2:
            if "support" not in metrics:
                errors.append("%s: schema v2 requires 'support' field" % split)
            elif not isinstance(metrics["support"], dict):
                errors.append("%s.support: must be a dictionary" % split)
            else:
                support = metrics["support"]
                for key in ["positive", "negative"]:
                    if key not in support:
                        errors.append("%s.support: missing '%s' count" % (split, key))
                    elif not isinstance(support[key], int):
                        errors.append("%s.support.%s: must be an integer" % (split, key))

    if len(errors) == 0:
        return True, errors
    return False, errors


def validate_artifact(artifact_path, artifact_type, schema_version=1, instances_path=None):
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
        print("Error: %s does not exist" % artifact_path, file=sys.stderr)
        return False

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print("Error: %s is not valid JSON: %s" % (artifact_path, e), file=sys.stderr)
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
        print("Error: Unknown artifact type '%s'" % artifact_type, file=sys.stderr)
        return False

    if not is_valid:
        print("Validation failed for %s:" % artifact_path, file=sys.stderr)
        for error in errors:
            print("  - %s" % error, file=sys.stderr)
        return False
    print("Validation passed: %s" % artifact_path)
    return True


# CLI entry point
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate pipeline artifacts")
    parser.add_argument("artifact_path", help="Path to artifact JSON file")
    parser.add_argument("--type", "-t", required=True, choices=["instances", "predictions", "metrics"], help="Artifact type to validate")
    parser.add_argument("--schema-version", type=int, default=1, choices=SCHEMA_VERSIONS, help="Schema version")
    parser.add_argument("--instances", help="Path to instances.json (predictions only)")

    args = parser.parse_args()
    success = validate_artifact(args.artifact_path, args.type, args.schema_version, args.instances)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
