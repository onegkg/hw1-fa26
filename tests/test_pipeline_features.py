"""Tests for pipeline features: RUN_TAG and SCHEMA_VERSION.

STUDENTS: These tests verify the Makefile plumbing you must implement.

The Python CLI commands already support --run-tag and --schema-version.
Your job is to wire these through the Makefile so that:
  make run-all RUN_TAG=myrun SCHEMA_VERSION=2
produces artifacts in build/myrun/ with schema v2 format.

Some tests will FAIL until you update the Makefile properly.
"""

import subprocess
from pathlib import Path

import pytest

from hw1.validate import validate_instances, validate_predictions, validate_metrics


class TestSchemaV1Validation:
    """Tests that schema v1 validation works correctly."""

    def test_valid_v1_instances(self):
        """Valid v1 instances should pass validation."""
        data = {
            "train": [{"tokens": ["good", "movie"], "label": 1}],
            "test": [{"tokens": ["bad", "film"], "label": 0}],
        }
        is_valid, errors = validate_instances(data, schema_version=1)
        assert is_valid, f"Should be valid: {errors}"

    def test_valid_v1_predictions(self):
        """Valid v1 predictions should pass validation."""
        data = {
            "train": [{"tokens": ["good"], "label": 1, "pred": 1}],
            "test": [{"tokens": ["bad"], "label": 0, "pred": 0}],
        }
        is_valid, errors = validate_predictions(data, schema_version=1)
        assert is_valid, f"Should be valid: {errors}"

    def test_valid_v1_metrics(self):
        """Valid v1 metrics should pass validation."""
        data = {
            "train": {"accuracy": 0.9, "precision": 0.85, "recall": 0.88, "f1": 0.86},
            "test": {"accuracy": 0.85, "precision": 0.82, "recall": 0.84, "f1": 0.83},
        }
        is_valid, errors = validate_metrics(data, schema_version=1)
        assert is_valid, f"Should be valid: {errors}"


class TestSchemaV2Validation:
    """Tests that schema v2 validation enforces additional requirements."""

    def test_v2_instances_requires_metadata(self):
        """Schema v2 instances must have metadata block."""
        data_without_metadata = {
            "train": [{"tokens": ["test"], "label": 1}],
            "test": [{"tokens": ["test"], "label": 0}],
        }
        is_valid, errors = validate_instances(data_without_metadata, schema_version=2)
        assert not is_valid, "Should fail without metadata"
        assert any("metadata" in e for e in errors)

    def test_v2_instances_with_metadata_passes(self):
        """Schema v2 instances with proper metadata should pass."""
        data = {
            "metadata": {"schema_version": 2},
            "train": [{"tokens": ["test"], "label": 1}],
            "test": [{"tokens": ["test"], "label": 0}],
        }
        is_valid, errors = validate_instances(data, schema_version=2)
        assert is_valid, f"Should be valid: {errors}"

    def test_v2_predictions_requires_confidence(self):
        """Schema v2 predictions must have confidence scores."""
        data_without_confidence = {
            "train": [{"tokens": ["test"], "label": 1, "pred": 1}],
            "test": [{"tokens": ["test"], "label": 0, "pred": 0}],
        }
        is_valid, errors = validate_predictions(data_without_confidence, schema_version=2)
        assert not is_valid, "Should fail without confidence"
        assert any("confidence" in e for e in errors)

    def test_v2_predictions_with_confidence_passes(self):
        """Schema v2 predictions with confidence should pass."""
        data = {
            "train": [{"tokens": ["test"], "label": 1, "pred": 1, "confidence": 0.85}],
            "test": [{"tokens": ["test"], "label": 0, "pred": 0, "confidence": 0.92}],
        }
        is_valid, errors = validate_predictions(data, schema_version=2)
        assert is_valid, f"Should be valid: {errors}"

    def test_v2_metrics_requires_support(self):
        """Schema v2 metrics must have support counts."""
        data_without_support = {
            "train": {"accuracy": 0.9, "precision": 0.85, "recall": 0.88, "f1": 0.86},
            "test": {"accuracy": 0.85, "precision": 0.82, "recall": 0.84, "f1": 0.83},
        }
        is_valid, errors = validate_metrics(data_without_support, schema_version=2)
        assert not is_valid, "Should fail without support"
        assert any("support" in e for e in errors)

    def test_v2_metrics_with_support_passes(self):
        """Schema v2 metrics with support should pass."""
        data = {
            "train": {
                "accuracy": 0.9, "precision": 0.85, "recall": 0.88, "f1": 0.86,
                "support": {"positive": 100, "negative": 100},
            },
            "test": {
                "accuracy": 0.85, "precision": 0.82, "recall": 0.84, "f1": 0.83,
                "support": {"positive": 50, "negative": 50},
            },
        }
        is_valid, errors = validate_metrics(data, schema_version=2)
        assert is_valid, f"Should be valid: {errors}"


class TestMakefileRunTagPlumbing:
    """Tests that Makefile properly passes RUN_TAG to commands.

    STUDENTS: These tests will FAIL until you update the Makefile to:
    1. Accept RUN_TAG variable (e.g., RUN_TAG ?= default)
    2. Pass --run-tag $(RUN_TAG) to all pipeline commands
    3. Update artifact paths to use build/$(RUN_TAG)/
    """

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent

    def test_make_run_all_with_custom_run_tag(self, project_root, tmp_path):
        """Running make with RUN_TAG should create artifacts in tagged subdirectory."""
        run_tag = "test_run_123"

        # Run make with custom RUN_TAG
        result = subprocess.run(
            ["make", "run-all", f"RUN_TAG={run_tag}", "DATA_DIR=tests/fixtures"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        # Check that artifacts were created in the tagged subdirectory
        tagged_dir = project_root / "build" / run_tag
        assert tagged_dir.exists(), (
            f"Expected build/{run_tag}/ directory to exist. "
            f"Update Makefile to pass --run-tag $(RUN_TAG) to commands. "
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Check that all expected artifacts exist
        for artifact in ["instances.json", "predictions.json", "metrics.json"]:
            artifact_path = tagged_dir / artifact
            assert artifact_path.exists(), (
                f"Expected {artifact} in build/{run_tag}/. "
                f"Make sure all commands use --run-tag $(RUN_TAG)."
            )


class TestMakefileSchemaVersionPlumbing:
    """Tests that Makefile properly passes SCHEMA_VERSION to commands.

    STUDENTS: These tests will FAIL until you update the Makefile to:
    1. Accept SCHEMA_VERSION variable (e.g., SCHEMA_VERSION ?= 1)
    2. Pass --schema-version $(SCHEMA_VERSION) to all pipeline commands
    """

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent

    def test_make_run_all_with_schema_v2(self, project_root):
        """Running make with SCHEMA_VERSION=2 should produce v2 format artifacts."""
        import json

        run_tag = "schema_v2_test"

        # Clean first
        subprocess.run(["make", "clean"], cwd=project_root, capture_output=True)

        # Run make with schema version 2
        result = subprocess.run(
            ["make", "run-all", f"RUN_TAG={run_tag}", "SCHEMA_VERSION=2", "DATA_DIR=tests/fixtures"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        # Load and validate artifacts
        build_dir = project_root / "build" / run_tag

        # Check instances.json has metadata (schema v2)
        instances_path = build_dir / "instances.json"
        if instances_path.exists():
            with open(instances_path) as f:
                instances_data = json.load(f)
            assert "metadata" in instances_data, (
                "Schema v2 instances.json should have 'metadata' field. "
                "Make sure Makefile passes --schema-version $(SCHEMA_VERSION) to preprocess."
            )

        # Check predictions.json has confidence (schema v2)
        predictions_path = build_dir / "predictions.json"
        if predictions_path.exists():
            with open(predictions_path) as f:
                predictions_data = json.load(f)
            if predictions_data.get("train"):
                first_pred = predictions_data["train"][0]
                assert "confidence" in first_pred, (
                    "Schema v2 predictions should have 'confidence' field. "
                    "Make sure Makefile passes --schema-version $(SCHEMA_VERSION) to rule-based."
                )

        # Check metrics.json has support (schema v2)
        metrics_path = build_dir / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path) as f:
                metrics_data = json.load(f)
            if metrics_data.get("train"):
                assert "support" in metrics_data["train"], (
                    "Schema v2 metrics should have 'support' field. "
                    "Make sure Makefile passes --schema-version $(SCHEMA_VERSION) to evaluate."
                )
