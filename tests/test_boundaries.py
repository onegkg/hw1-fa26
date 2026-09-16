"""Tests for contract enforcement at pipeline stage boundaries (Task 6).

STUDENTS: Some of these tests will FAIL until each pipeline stage refuses an
invalid input artifact before it runs.

Each test builds the pipeline on the fixture data in a temporary copy of your
project, corrupts one intermediate artifact so that it breaks the documented
contract, and then runs the stage that consumes that artifact. The stage must
exit with an error and must not write its own output.

The schema v2 tests run the pipeline with SCHEMA_VERSION=2, so they rely on
your Task 4 changes.
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
ARTIFACTS = Path("build") / "default"
IGNORE = shutil.ignore_patterns(".git", ".venv", "build", "data", "__pycache__", "*_cache")


def make(project: Path, target: str, *variables: str) -> subprocess.CompletedProcess[str]:
    """Run one Makefile target on the fixture data."""
    return subprocess.run(
        ["make", target, "DATA_DIR=tests/fixtures", *variables],
        capture_output=True,
        text=True,
        cwd=project,
        timeout=300,
    )


def output_of(result: subprocess.CompletedProcess[str]) -> str:
    return f"exit code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"


@pytest.fixture(scope="module")
def built_pipeline(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    """A copy of the project with instances, predictions, and metrics already built."""
    base = tmp_path_factory.mktemp("boundaries") / "project"
    shutil.copytree(PROJECT_ROOT, base, ignore=IGNORE)
    result = make(base, "evaluate")
    return base, output_of(result)


@pytest.fixture(scope="module")
def built_pipeline_v2(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    """Like built_pipeline, but built with SCHEMA_VERSION=2."""
    base = tmp_path_factory.mktemp("boundaries_v2") / "project"
    shutil.copytree(PROJECT_ROOT, base, ignore=IGNORE)
    result = make(base, "evaluate", "SCHEMA_VERSION=2")
    return base, output_of(result)


def copy_project(built: tuple[Path, str], tmp_path: Path) -> Path:
    base, _ = built
    copy = tmp_path / "project"
    shutil.copytree(base, copy)  # copies modification times too, so Make sees it as up to date
    return copy


@pytest.fixture
def project(built_pipeline: tuple[Path, str], tmp_path: Path) -> Path:
    """A fresh copy of the built pipeline for one test to corrupt."""
    return copy_project(built_pipeline, tmp_path)


@pytest.fixture
def project_v2(built_pipeline_v2: tuple[Path, str], tmp_path: Path) -> Path:
    """A fresh copy of the schema v2 pipeline for one test to corrupt."""
    return copy_project(built_pipeline_v2, tmp_path)


def load_artifact(project: Path, name: str, built_pipeline: tuple[Path, str]) -> Any:
    path = project / ARTIFACTS / name
    assert path.exists(), (
        f"Expected build/default/{name} after `make evaluate` on valid fixture data, "
        f"before anything was corrupted. The pipeline must run cleanly on valid input "
        f"first.\n{built_pipeline[1]}"
    )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_artifact(project: Path, name: str, data: Any) -> None:
    with open(project / ARTIFACTS / name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def remove_outputs(project: Path, *names: str) -> None:
    for name in names:
        (project / ARTIFACTS / name).unlink(missing_ok=True)


def assert_refused(
    result: subprocess.CompletedProcess[str], project: Path, target: str, output: str
) -> None:
    assert result.returncode != 0, (
        f"`make {target}` succeeded on a corrupted input artifact. The stage should "
        f"validate its input and stop with an error.\n{output_of(result)}"
    )
    assert not (project / ARTIFACTS / output).exists(), (
        f"`make {target}` failed, but still wrote build/default/{output}. Check the "
        f"input before the stage runs, so no output is produced from invalid input."
    )


class TestBoundaryContracts:
    """Each stage must refuse an input artifact that breaks the contract."""

    def test_pipeline_accepts_valid_artifacts(
        self, project: Path, built_pipeline: tuple[Path, str]
    ) -> None:
        """Boundary checks must not reject the pipeline's own valid artifacts."""
        load_artifact(project, "metrics.json", built_pipeline)
        remove_outputs(project, "evaluation_plot.png")
        result = make(project, "plot")
        assert result.returncode == 0, (
            f"`make plot` failed on artifacts the pipeline just produced.\n{output_of(result)}"
        )

    def test_rule_based_rejects_invalid_instances(
        self, project: Path, built_pipeline: tuple[Path, str]
    ) -> None:
        """preprocess -> rule-based: a label outside {0, 1} must be refused."""
        data = load_artifact(project, "instances.json", built_pipeline)
        data["train"][0]["label"] = 5
        save_artifact(project, "instances.json", data)
        remove_outputs(project, "predictions.json", "metrics.json")

        result = make(project, "rule-based")
        assert_refused(result, project, "rule-based", "predictions.json")

    def test_evaluate_rejects_invalid_predictions(
        self, project: Path, built_pipeline: tuple[Path, str]
    ) -> None:
        """rule-based -> evaluate: a prediction outside {0, 1} must be refused."""
        data = load_artifact(project, "predictions.json", built_pipeline)
        data["test"][0]["pred"] = 2
        save_artifact(project, "predictions.json", data)
        remove_outputs(project, "metrics.json")

        result = make(project, "evaluate")
        assert_refused(result, project, "evaluate", "metrics.json")

    def test_evaluate_rejects_boolean_predictions(
        self, project: Path, built_pipeline: tuple[Path, str]
    ) -> None:
        """rule-based -> evaluate: predictions must be the integers 0 or 1, not true/false."""
        data = load_artifact(project, "predictions.json", built_pipeline)
        for split in ("train", "test"):
            for inst in data[split]:
                inst["pred"] = bool(inst["pred"])
        save_artifact(project, "predictions.json", data)
        remove_outputs(project, "metrics.json")

        result = make(project, "evaluate")
        assert_refused(result, project, "evaluate", "metrics.json")

    def test_evaluate_rejects_missing_prediction(
        self, project: Path, built_pipeline: tuple[Path, str]
    ) -> None:
        """rule-based -> evaluate: there must be one prediction for every instance."""
        data = load_artifact(project, "predictions.json", built_pipeline)
        data["test"].pop()
        save_artifact(project, "predictions.json", data)
        remove_outputs(project, "metrics.json")

        result = make(project, "evaluate")
        assert_refused(result, project, "evaluate", "metrics.json")

    def test_rule_based_rejects_v1_instances_in_v2_run(
        self, project_v2: Path, built_pipeline_v2: tuple[Path, str]
    ) -> None:
        """preprocess -> rule-based (schema v2): instances without v2 metadata must be refused."""
        data = load_artifact(project_v2, "instances.json", built_pipeline_v2)
        assert "metadata" in data, (
            "instances.json from `make evaluate SCHEMA_VERSION=2` has no 'metadata' block, "
            "so it isn't a schema v2 artifact. Is SCHEMA_VERSION passed through the "
            "Makefile (Task 4)?"
        )
        del data["metadata"]
        save_artifact(project_v2, "instances.json", data)
        remove_outputs(project_v2, "predictions.json", "metrics.json")

        result = make(project_v2, "rule-based", "SCHEMA_VERSION=2")
        assert_refused(result, project_v2, "rule-based", "predictions.json")

    def test_evaluate_rejects_v1_predictions_in_v2_run(
        self, project_v2: Path, built_pipeline_v2: tuple[Path, str]
    ) -> None:
        """rule-based -> evaluate (schema v2): predictions without confidence must be refused."""
        data = load_artifact(project_v2, "predictions.json", built_pipeline_v2)
        for split in ("train", "test"):
            for inst in data[split]:
                inst.pop("confidence", None)
        save_artifact(project_v2, "predictions.json", data)
        remove_outputs(project_v2, "metrics.json")

        result = make(project_v2, "evaluate", "SCHEMA_VERSION=2")
        assert_refused(result, project_v2, "evaluate", "metrics.json")

    def test_plot_rejects_invalid_metrics(
        self, project: Path, built_pipeline: tuple[Path, str]
    ) -> None:
        """evaluate -> plot: negative metric values must be refused."""
        data = load_artifact(project, "metrics.json", built_pipeline)
        for split in ("train", "test"):
            for name, value in data[split].items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    data[split][name] = -1.0
        save_artifact(project, "metrics.json", data)
        remove_outputs(project, "evaluation_plot.png")

        result = make(project, "plot")
        assert_refused(result, project, "plot", "evaluation_plot.png")
