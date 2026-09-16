# HW1: Pipeline Automation & Build Systems

This assignment teaches automation fundamentals for project builds through an NLP sentiment analysis pipeline. You'll work with **Makefiles**, **linting/type-checking**, **Bash scripting**, and **CI/CD**—skills essential for nearly any production codebase.

**ASSIGNMENT DUE DATE (all parts):** Monday, Sept 28th @ 11:59pm ET

## Learning Objectives

By completing this assignment, you will:

1. **Work with strict code quality tools** (ruff, mypy, shellcheck) that encode a team's coding standards, in both Python and Bash (Tasks 1–3)
2. **Use automated fixes with judgment**: decide which fixes can be trusted as-is and which need review, reverting, or declining (Tasks 1 and 3)
3. **Add type annotations** as a contract the language itself can enforce (Task 2)
4. **Understand build automation** by wiring parameters through a Makefile that orchestrates a multi-stage pipeline (Task 4)
5. **Reason about and enforce contracts between components**: gather evidence about what a contract is supposed to be, resolve a disagreement, and check contracts where one stage hands off to the next (Tasks 5 and 6)
6. **Experience CI/CD feedback loops** via GitHub Actions and the Gradescope autograder (Task 7)

## Orchestration, abstraction, and contracts

Modern software pipelines involve multiple "languages" (Python, Bash) that must work together. Many projects have explicit orchestration scripts that determine how these components will interface with each other and what processes are exposed to a user. Individual components are typically communicating through intermediate files with agreed-upon formats and CLI flags passed between stages, with an either implicit or explicit **contract** or schema those files must follow.

In this assignment:
- **Python** implements the ML pipeline logic (already done for you, but needs cleanup)
- **Make** orchestrates the pipeline stages (you wire it together)
- **Python validators** (`hw1.validate`) check artifacts against their contracts, and a **Bash** script runs the final validation
- **JSON artifact formats** (schema v1 and v2) are the contracts between stages

Your job is to make all these pieces work together *reliably*.

---

## CI/CD
**Continuous Integration / Continuous Delivery (CI/CD)** refers to the practice of automatically running checks—such as linting, type-checking, tests, and full pipeline runs—whenever code changes are pushed to a shared repository. In this project, CI is implemented using **GitHub Actions**, which defines a set of automated jobs in a workflow file (e.g., [`ci.yml`](.github/workflows/ci.yml)). Each job runs inside the same Docker image you develop in, and Gradescope runs the same checks when you submit. These jobs encode the *automation policy* for the repository: what “correct,” “clean,” and “complete” mean in an enforceable way. You may not see a single obvious command that runs *all* CI checks locally, and that is intentional. You have several options: you can set up a local workflow that mirrors CI (there are many ways to do this), or you can read the CI configuration file to see exactly which commands are being run and invoke those commands yourself. Part of the goal of this assignment is to help you learn how to *read and reason about automation systems*, not just use them passively.

### Running CI on GitHub

In most projects, CI runs automatically every time someone pushes. **In this course it only runs when you start it yourself.** Your repository is private, and GitHub Actions minutes for private repositories come out of your personal GitHub account's free monthly quota, which you may need for other courses. So do your checking in the container, and run CI on GitHub when you want to confirm your pushed work.

**Run the CI checks locally before you push.** This is good practice in any project, because it keeps broken work out of the shared repository, and it matters even more here. The commands CI runs are listed in [`ci.yml`](.github/workflows/ci.yml), and every one of them works the same way in your container. Then, to run CI on GitHub:

1. Push your commits to GitHub.
2. On your repository's GitHub page, open the **Actions** tab.
3. Choose the **CI** workflow in the list on the left.
4. Click **Run workflow**, keep the branch set to `main`, and click the green **Run workflow** button.
5. After a few seconds a new run appears; click it to watch each job and read its output.

Each run uses a few minutes of your quota, so run it when you have something to confirm, not after every commit. The comments at the top of [`ci.yml`](.github/workflows/ci.yml) show what the usual automatic trigger looks like.


## Assignment Structure

This assignment has three parts:

| Part | Where | Description |
|------|-------|-------------|
| **Artifact** | [ARTIFACT.md](ARTIFACT.md) | Fix the codebase to make CI pass; submitted to **HW1 Artifact** on Gradescope |
| **Written Reflection** | [WRITTEN.md](WRITTEN.md) | Reflect on your process and connect to course themes; submitted to **HW1 Written** on Gradescope |
| **AI Usage Report** | [HW1 AI usage reporting tool](https://genai.cs.brandeis.edu/prompt/e3907588-896b-403f-9076-908b87127a68) | Required **even if you didn't use AI** |

**Complete the artifact first**, then write your reflection. The written component asks you to reflect on your experience completing the artifact, so it should be done after the artifact. 

AI usage reporting should come last. Full instructions for reporting AI usage can be found on Moodle.

---

## Required Reading

Before starting the written reflection, read:

- **Peter Naur, "Programming as Theory Building"** (provided on Moodle)
- **Ursula Franklin, "The Real World of Technology"** from page 17 "Let's distinguish..." to the end of page 23 "...the way it's done today around the globe" (link on Moodle)

This reading is essential for the written reflection.

---

## Prerequisites & Setup

### Getting your repository

You work in your own **private** copy of the assignment:

1. Go to <https://github.com/brandeis-cosi-106b/hw1-fa26> and click **Use this template → Create a new repository**.
2. Set **Owner** to your own GitHub account, name it (for example `cosi106b-hw1`), and choose **Private**. Your repository must be private, since public repositories let other students see your work.
3. Click **Create repository**, then clone *your* new repository (not `brandeis-cosi-106b/hw1-fa26`) to your computer.

Your copy starts with a single commit and isn't linked to the course repository, so it won't receive changes automatically. See [Required updates](#required-updates) for how to get them.

### Required updates

In the event that bugs in the assignment are discovered after release, course staff may publish fixes to the assignment. **Applying them is required.** They will be announced with one or more commit IDs. In your repository, inside the container terminal:

```bash
git remote add upstream https://github.com/brandeis-cosi-106b/hw1-fa26.git   # first time only
git fetch upstream
git cherry-pick <commit-id>          # as announced
git push
```

If Git reports a conflict, it's because you edited the same lines as the fix. Open the listed files, keep both your work and the fix, then run `git add <file>` and `git cherry-pick --continue`. Don't use `git merge` or `git pull` with `upstream`: your repository shares no history with it, so every file you changed would conflict. The Gradescope autograder always checks against the updated version, so a fix you skip can make it fail.

### Tools

All work for this course happens inside a **Docker development container** with
every tool preinstalled (Python 3.11, Make, shellcheck, ruff, mypy, pytest, and
the pipeline's Python packages), at exactly the versions that GitHub Actions and
Gradescope use. It works the same on macOS, Windows, and Linux, and you **don't**
need to install any of them yourself.

**Follow [DOCKER.md](DOCKER.md) to get set up.** In short: install **Docker
Desktop** and **VS Code** with the Dev Containers extension (about 20 minutes, once,
reused for every assignment; no Docker account needed), then open this repository
in the container. If Docker won't run on your computer, DOCKER.md describes a
browser-based fallback.

Once your container is open, check in its terminal that everything is there:

```bash
make --version
ruff --version
mypy --version
```

The Python packages are declared in `pyproject.toml`, with exact versions pinned in `uv.lock`:

| Package | Purpose |
|---------|---------|
| **ruff** | Fast Python linter |
| **mypy** | Static type checker |
| **pytest** | Test framework |
| **click** | CLI framework (used by the NLP pipeline) |
| **matplotlib** | Plotting library (used by the NLP pipeline) |
| **textblob** | Sentiment lexicon (used by the rule-based classifier) |

> **Prefer to install tools natively?** You can, but it's unsupported: if your
> results differ from CI or Gradescope, the container is the reference. The
> exact versions are pinned in [`.devcontainer/install-tools.sh`](.devcontainer/install-tools.sh).

See [ARTIFACT.md](ARTIFACT.md) for additional setup instructions, including downloading the IMDB dataset.

---

## Grading

This assignment is evaluated using **two independent letter grades**:

| Grade | Evaluates |
|-------|-----------|
| **Artifact Grade** | Technical execution, engagement with automation tools, good-faith effort |
| **Reflection Grade** | Theory-building, honest self-assessment, engagement with course ideas |

These grades are **not mechanically averaged**. Strong performance in one area does not automatically compensate for the other—but for HW1, a strong written reflection can meaningfully offset incomplete technical execution.

**See [RUBRIC.md](RUBRIC.md) for detailed grading criteria.**

### What We're Looking For

**Artifact**: Aim for passing CI, but we also value *engagement* and *intentionality*. Did you understand what you were fixing, and did you know which automated fixes could be trusted and which needed a closer look? Did you wire the Makefile thoughtfully, or copy-paste without understanding? The self-assessment in your written reflection helps us see this.

Note: It may be the case that you can make a good argument for "just" using the automation tools at your disposal. I do not recommend this, but if you intend to do this, I recommend reading over the written reflection questions first to ensure that you will still be able to answer all of them appropriately.

**Reflection**: We value honesty, specificity, and genuine engagement with course ideas - especially with the readings for this assignment listed above. A thoughtful reflection on partial success is more valuable than a superficial reflection on complete success.

### CI Jobs

The following CI jobs run each time you run the CI workflow (see [Running CI on GitHub](#running-ci-on-github)):

1. **quality**: `ruff check` and `mypy` pass with no errors
2. **shell**: `shellcheck` passes on all scripts
3. **tests**: All pytest tests pass (including the Makefile plumbing and stage boundary tests)
4. **pipeline**: `make run-all` completes successfully with fixtures

Passing all CI jobs is a strong signal of artifact completion, but is not the sole criterion for grading.

### Gradescope Autograder

When you submit your artifact to Gradescope, it runs the **same checks** as the CI jobs above, one Gradescope test per job, and shows you the exact command and its output for each. It also has one test each for Task 5 and Task 6, and reports whether it found your evidence screenshot (not scored). Two differences from GitHub Actions:

- Every check runs, even if an earlier one fails, so you get feedback on everything at once.
- The autograder uses the **original** tests and the original ruff/mypy settings. Editing `tests/` or loosening the settings in `pyproject.toml` won't change your autograder results (and will be visible to course staff).

The autograder score is **not** your artifact grade. It's one piece of evidence course staff use alongside [RUBRIC.md](RUBRIC.md).

---

## AI Tools Policy

You may use automation tools to help with this assignment, including both LLM-powered tools and other "older" automations (e.g., built into your IDE). You must document your usage in the written reflection (Part 1C) and in the AI usage report (see [Assignment Structure](#assignment-structure)).

LLM tools are particularly helpful for understanding error messages (e.g, from linters/type checkers) and basic syntax, but documentation is still your friend if you have a question about a particular tool. You may find useful tips that you didn't even realize you should look for.

**Remember**: LLM tools can also help you write code, but you need to understand what it's doing. The written reflection will ask you to reflect on how you used these tools—and you may be asked about your submission in an oral exam.

---

## Submission

Your final repository should contain:

| File | Description |
|------|-------------|
| **All source files** | With lint errors fixed and type annotations added |
| **Makefile** | With RUN_TAG and SCHEMA_VERSION properly wired, and input checks before each stage |
| **scripts/validate_pipeline.sh** | With shellcheck violations fixed |
| **Contract fixes** | Your Task 5 resolution and Task 6 boundary checks, wherever you made them |
| **evidence.png** (or similar) | Screenshot of successful pipeline run on full dataset |

### How to Submit

0. Review [RUBRIC.md](RUBRIC.md) to understand how you'll be evaluated
1. Complete the steps required in [ARTIFACT.md](ARTIFACT.md) (aim for all CI checks to pass)
2. Run the pipeline on the full IMDB dataset and capture evidence
3. Commit and push:

```bash
git add -A
git commit -m "Complete HW1: pipeline automation"
git push
```

4. Verify on GitHub:
   - Run the CI workflow ([Running CI on GitHub](#running-ci-on-github)) and confirm all jobs pass
   - Confirm that `evidence.png` is visible in your repository

5. Submit your **artifact** on Gradescope: open the **HW1 Artifact** assignment, choose **GitHub** as the submission method, and select your HW1 repository and the `main` branch. The autograder results appear within a few minutes. You can resubmit as many times as you like before the deadline; your last submission is the one graded.

6. Complete the written reflection in [WRITTEN.md](WRITTEN.md) (including the self-assessment), then upload your completed `WRITTEN.md` to the **HW1 Written** assignment on Gradescope.

7. Submit your AI usage report through the [HW1 AI usage reporting tool](https://genai.cs.brandeis.edu/prompt/e3907588-896b-403f-9076-908b87127a68), **even if you didn't use AI**. Full instructions for reporting AI usage can be found on Moodle.

---

## Resources

- [Click documentation](https://click.palletsprojects.com/)
- [GNU Make manual](https://www.gnu.org/software/make/manual/)
- [ruff documentation](https://docs.astral.sh/ruff/), including [fix safety](https://docs.astral.sh/ruff/linter/#fix-safety) (safe vs. unsafe fixes)
- [`git restore` documentation](https://git-scm.com/docs/git-restore) (undoing changes you haven't committed)
- [mypy documentation](https://mypy.readthedocs.io/)
- [shellcheck wiki](https://www.shellcheck.net/wiki/)
