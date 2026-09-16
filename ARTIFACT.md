# Artifact Instructions

This document describes the technical work required for HW1.

---

## Current State: CI is Failing

When you clone this repo, **CI will fail** (CI runs only when you start it; see "Running CI on GitHub" in [README.md](README.md#running-ci-on-github)). This is intentional. The codebase was written in a style that a naive code generator might produce (and in fact did produce)—functional but not conforming to the project's strict quality standards.

**Your goal**: Work through these issues to make CI pass. Passing CI is a strong signal of completion, but we also value *engagement* and *understanding*—see [RUBRIC.md](RUBRIC.md) for how this work is evaluated.

---

## Setup

> **Prerequisites**: Open this repository in the course dev container. See [DOCKER.md](DOCKER.md). Run every command below in the container's terminal. Python, Make, shellcheck, ruff, mypy, pytest, and all of the pipeline's Python packages are already installed there, so there is nothing else to install.

### Download the IMDB dataset (for local testing)

Download the IMDB movie review dataset from Moodle (`imdb-review.zip`), unzip it, and place the `data/` directory in the repo root:

```
hw1/
├── data/           # Your local dataset (not committed)
│   ├── train/
│   │   ├── pos/
│   │   └── neg/
│   └── test/
│       ├── pos/
│       └── neg/
├── src/
├── tests/
└── ...
```

> **Note**: CI uses a tiny fixture dataset in `tests/fixtures/`. You should test locally with the full dataset before submitting.

---

## Tasks

### Task 1: Fix Linting Errors (~115 violations)

Run the linter:
```bash
make lint          # runs: ruff check src/
```

The codebase uses several patterns that violate our strict lint rules. In many real-world settings, you would not be allowed to push this code out to production until these were fixed, so you're gonna fix them.

You don't have to fix all of them by hand: ruff can fix many violations automatically. But an automatic fix is still a change to your code that you didn't write, so look at each one before you keep it.

**Commit your work before using any auto-fix**, so you have something to go back to:

```bash
git add -A
git commit -m "Before ruff auto-fix"
```

1. **Apply the safe fixes.** `ruff check src/ --fix` applies only the fixes ruff considers *safe*, meaning they shouldn't change what the code does. Review what it changed with `git diff`.
2. **Undo anything you don't want.** `git restore src/` discards every uncommitted change under `src/`; `git restore src/hw1/utils.py` discards the changes to just that file. (`git checkout -- <path>` does the same thing.)
3. **Go through the unsafe fixes one rule at a time.** After `--fix`, ruff reports how many "hidden fixes" it did *not* apply because they might change behavior. You can preview the fixes for a single rule without changing anything, then apply only that rule:

   ```bash
   ruff check src/ --select UP031 --unsafe-fixes --diff   # preview UP031's fixes
   ruff check src/ --select UP031 --unsafe-fixes --fix    # apply only UP031's fixes
   ruff rule UP031                                        # what the rule checks, and why
   ```

   For each rule, decide whether its fix is one you'd accept.

**One exception: leave the `B905` violation** (`zip()` without an explicit `strict=`) **for Task 6**, and don't apply ruff's automatic fix for it. The code it flags is part of what you'll work on in Task 6, which should make clear why ruff marks this fix as unsafe.

Whatever ruff can't fix at all (long lines, for example) is yours to fix by hand.

### Task 2: Add Type Annotations (~25 functions)

Run the type checker:
```bash
make typecheck     # runs: mypy
```

**The codebase has NO type annotations on functions.** You must add them to satisfy strict mypy settings:

```python
# Before (fails mypy)
def tokenize(text):
    ...

# After (passes mypy)
def tokenize(text: str) -> list[str]:
    ...
```

Remember, types are one kind of contract that a programming language can enforce between different components of a system. They only go so far, but they help catch bugs along the way. Did you find any?

Files to annotate:
- `src/hw1/dataset.py` - Data loading and preprocessing functions
- `src/hw1/models.py` - Classifier classes and methods
- `src/hw1/evaluation.py` - Metric computation functions
- `src/hw1/utils.py` - Plotting utilities
- `src/hw1/validate.py` - Artifact validation functions

**Tip:** Look at the docstrings—they describe what types each function expects and returns. Use modern Python 3.11+ syntax (`list[str]` not `List[str]`).

### Task 3: Fix Shell Script Errors (~30 findings)

The shell script has intentional shellcheck violations. Run shellcheck in your container to see them (the `shell` job in CI runs the same check):

```bash
shellcheck scripts/validate_pipeline.sh
```

You are likely not as familiar with Bash as you are Python, but you are almost certainly familiar enough with programming in general to have a sense of what Bash is doing. Use the documentation to help make sense of the specific errors shellcheck produces.

shellcheck can also suggest fixes for some findings, printed as a diff that Git can apply. Use the same routine as in Task 1: commit first, apply, review, and undo what you don't want.

```bash
shellcheck -f diff scripts/validate_pipeline.sh | git apply                  # apply every suggested fix
git diff scripts/                                                            # review the changes
git restore scripts/validate_pipeline.sh                                     # undo them
shellcheck --include=SC2086 -f diff scripts/validate_pipeline.sh | git apply # apply fixes for one code only
```

Unlike ruff, shellcheck doesn't label its fixes safe or unsafe, so that judgment is yours. For example, putting quotes around a variable is usually right, but not when the variable is *meant* to expand into several words or a filename pattern. Each code has a wiki page explaining its reasoning (e.g. <https://www.shellcheck.net/wiki/SC2086>).

### Task 4: Wire RUN_TAG and SCHEMA_VERSION Through Makefile

Each pipeline stage is a Python module with a command-line interface, run as `python -m hw1.<module>`. The Makefile gives each stage a name (`preprocess`, `rule-based`, `evaluate`, `plot`) and declares how the stages depend on each other. Try one directly:

```bash
PYTHONPATH=src python -m hw1.dataset --help
```

(The Makefile sets `PYTHONPATH` for you, so Python can find the `hw1` package in `src/`.)

You should see `--run-tag` and `--schema-version` options. These are already implemented in Python, but the Makefile never passes them. Your job is to **plumb them through the Makefile** so users can run:

```bash
make run-all RUN_TAG=experiment1 SCHEMA_VERSION=2
```

And have artifacts created in `build/experiment1/` with schema v2 format.

**What to do in the Makefile:**

1. Uncomment the `RUN_TAG` and `SCHEMA_VERSION` variables
2. Update `ARTIFACTS_DIR` to use `$(RUN_TAG)` instead of hardcoded "default"
3. Add `--run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)` to each pipeline command that accepts them (check each command's `--help`)

**Example of what a command should look like after your changes:**
```makefile
$(INSTANCES): | $(ARTIFACTS_DIR)
	python -m hw1.dataset $(DATA_DIR) --output $(OUTPUT_DIR) --run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)
```

### Task 5: Resolve a Contract Mismatch

With Tasks 1–4 done, run the pipeline:

```bash
make run-all
```

It fails. The stages run, but two parts of the pipeline disagree about what one of the artifacts contains. Neither side is "crashing"; each is doing exactly what it was written to do.

Find the disagreement and resolve it. Before you change anything, gather evidence about what the contract is *supposed* to be: docstrings, unit tests, the validator, the stages that consume the artifact, and the tool output itself. Then decide which side is wrong, and fix that side.

There is more than one defensible resolution, and the autograder accepts more than one, but not every one. Whatever you decide, the pipeline must still be able to *detect* this kind of mismatch if it happens again: a check that would accept either reading isn't enforcing a contract. Keep notes on the evidence you used and the choice you made; WRITTEN.md asks about both.

### Task 6: Enforce Contracts at Every Boundary

`make validate` checks the artifacts at the very end, after every stage has already run on whatever the previous stage handed it. Some stages in the Makefile also check their input first, but not all of them do, and a check that runs is not necessarily a check that enforces the contract. There are three boundaries where one stage's output becomes the next stage's input:

| Artifact | Produced by | Consumed by |
|---|---|---|
| `instances.json` | `preprocess` | `rule-based` |
| `predictions.json` | `rule-based` | `evaluate` |
| `metrics.json` | `evaluate` | `plot` |

Change the pipeline so that **each stage checks its input artifact against the contract before it runs**. A bad artifact should stop the pipeline at the boundary it crossed: the stage exits with an error and does not write its own output. How you do this is up to you (in the Makefile, in Python, or both), as long as `make rule-based`, `make evaluate`, and `make plot` behave this way.

The tests in `tests/test_boundaries.py` corrupt one intermediate artifact at a time and check that the next stage refuses it:

```bash
pytest tests/test_boundaries.py -v
```

Some of these tests build the pipeline with `SCHEMA_VERSION=2`, so they rely on your work from Task 4. This is also the task where you resolve the `B905` violation you left in Task 1.

If a test still fails after you've added the checks, look at what the corrupted artifact actually contains and compare it with the *documented* contract (docstrings, field descriptions), not only with what the validator currently checks. A contract that nothing enforces is easy to break without noticing, including by code that "works". Make sure your checks also hold up when you run with `SCHEMA_VERSION=2`.

### Task 7: Run Tests and Verify

```bash
make test          # runs: pytest tests/ -v
```

All tests should pass, including the Makefile plumbing tests in `tests/test_pipeline_features.py` and the boundary tests in `tests/test_boundaries.py`.

Once everything passes in your container, push your work and run the CI workflow on GitHub to confirm (see "Running CI on GitHub" in [README.md](README.md#running-ci-on-github)).

### Task 8: Local Evidence (Full Dataset)

Before submitting, run the pipeline on the full IMDB dataset:

```bash
make clean
make run-all DATA_DIR=data RUN_TAG=local_full SCHEMA_VERSION=2
```

Take a screenshot of the successful completion and metrics output. Include this in your submission (add as `evidence.png` or similar).

---

## Tips

- Run `make quality` frequently as you code
- Read error messages carefully—they often tell you exactly what to fix
- The CLI commands have good `--help` output; use it to understand the options
- Don't change the command-line interface of the pipeline stages (arguments and options): the autograder runs some stages directly
- For type annotations, read the docstrings—they describe expected types
- Don't modify `.github/workflows/ci.yml`: the Gradescope autograder runs the original checks regardless, and reports changes to it for course staff

---

## File Structure

```
hw1/
├── .devcontainer/         # Docker dev environment (see DOCKER.md)
├── .github/workflows/     # CI configuration (DO NOT MODIFY)
│   └── ci.yml            # CI workflow (run it by hand from the Actions tab)
├── scripts/
│   └── validate_pipeline.sh   # Bash validation script (FIX shellcheck errors)
├── src/hw1/
│   ├── __init__.py
│   ├── dataset.py        # Data preprocessing (ADD type annotations, FIX lint)
│   ├── models.py         # Classifiers (ADD type annotations, FIX lint)
│   ├── evaluation.py     # Metrics computation (ADD type annotations, FIX lint)
│   ├── utils.py          # Plotting utilities (ADD type annotations, FIX lint)
│   └── validate.py       # Artifact validation (ADD type annotations, FIX lint)
├── tests/
│   ├── fixtures/         # Tiny test dataset for CI
│   ├── test_dataset.py
│   ├── test_models.py
│   ├── test_evaluation.py
│   ├── test_utils.py
│   ├── test_boundaries.py        # Tests for contract checks between stages
│   └── test_pipeline_features.py  # Tests for Makefile plumbing
├── Makefile              # Build automation (ADD RUN_TAG/SCHEMA_VERSION plumbing)
├── pyproject.toml        # Dependencies + ruff/mypy/pytest settings (don't loosen these)
└── uv.lock               # Exact package versions installed in the container
```
