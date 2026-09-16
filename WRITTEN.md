# HW1 Written Reflection

Answer the following questions thoughtfully. There are no "right" answers—the goal is genuine reflection on your experience and engagement with the ideas from class.

This written component is designed to reward **honest engagement and theory-building**, even if your artifact is incomplete. A working pipeline without understanding and a partial pipeline with deep understanding are *not* the same thing—but both can be discussed thoughtfully here.

---

## Part 0: Self-Assessment

Complete this section **before** writing your reflection. Be honest—this is not penalized and helps us calibrate grading. Accurate self-assessment demonstrates the kind of self-awareness we value.

### Artifact Completion

For each task, mark your status: **Done**, **Partial**, or **Not Done**. Add brief notes if helpful.

| Task | Status | Notes (optional) |
|------|--------|------------------|
| 1. Lint errors fixed (`ruff check` passes) | | |
| 2. Type annotations added (`mypy` passes) | | |
| 3. Shell script fixed (`shellcheck` passes) | | |
| 4. Makefile wires `RUN_TAG` and `SCHEMA_VERSION` correctly | | |
| 5. Contract mismatch resolved (`make run-all` passes) | | |
| 6. Contracts enforced at every boundary (`tests/test_boundaries.py` passes) | | |
| 7. All CI jobs pass | | |
| 8. Local evidence screenshot included | | |

### Understanding Self-Check

Answer briefly (1–3 sentences each):

1. **What do you feel you genuinely understand** about this assignment? (Not just "made it work," but could explain to someone else or extend on your own.)

2. **What did you make work without fully understanding?** (Be honest—this is valuable self-knowledge.)

3. **Where did you get stuck?** What did you try before moving on or seeking help?

---

## Part 1: Short Response (1 paragraph each)

### A: Your Path Through the Assignment

Briefly describe how you approached this assignment. Did you try to build a mental model of how the pipeline worked before fixing it? Did you focus primarily on satisfying tools like `ruff`, `mypy`, or the Makefile? Did your approach change over time?

There is no wrong answer—be honest about what you actually did, not what you think you *should* have done.

### B: Friction and Flow

Which parts of this assignment felt like *productive friction* (friction that forced you to learn something valuable), and which felt like *unproductive friction* (busywork, confusion, or tool pain that didn't help)? Be specific about where those moments occurred.

### C: Automation Tools

Which automated fixes did you apply, and which did you review, undo, or decline? How did you decide which ones to trust?

If you used LLM-powered tools, what did you use them for? What did they do well? Where did they fail, mislead you, or require careful verification? If you instead chose to do everything by hand, where do you wish automation would have helped?

---

## Part 2: Course Connections (1–2 paragraphs each)

### A: Designs for Compliance (Franklin)

In the assigned pages, Franklin walks through how a Shang Dynasty foundry cast a bronze vessel, including the different roles of the designer and model builder and of the potter who made the molds. Look back at what she says each of those roles needed to know, and how much room each had for their own judgement.

Where in this assignment did you work like the potter, and where, if anywhere, did you work like the model builder? Who laid down the prescriptions you followed, and who benefits from software work being organized this way?

### B: Abstractions as Contracts (Liskov)

Barbara Liskov presented the idea that components should interact through well-defined contracts—agreements about inputs, outputs, and behavior—rather than relying on implementation details. We've seen this pattern in multiple technologies so far, with abstraction layers adhering to contracts that simultaneously *enforce* constraints while *enabling* other capabilities (e.g., LLVM IR constraining the compiler target output while enabling portability).

Where did the contracts in this assignment (CLI flags, file formats, Makefile targets, validation steps) constrain you, and what did those constraints enable? Then consider the cost: is making every contract explicit and enforced always worth it? Describe a case, in this pipeline or elsewhere, where you would leave a contract implicit, and why.

---

## Part 3: Resolving a Contract Mismatch (1–2 paragraphs)

In Task 5, two parts of the pipeline disagreed about what an artifact contains. Which side did you change, and what evidence led you there? Would you have chosen the same contract if the design were entirely up to you, and, given that the autograder accepts some resolutions but not others, how much of that decision was really yours to make?

---

## Part 4: Essay — Theory Building and Modern Development (500–700 words)

*This is the biggest question, in terms of both size and importance. Take your time with it.*

Peter Naur argues in **"Programming as Theory Building"** that the essence of programming is not the code itself, but the *theory* the programmer builds—a mental model connecting the problem, the solution, and the code. Code without its accompanying theory may run, but it cannot be easily understood, maintained, or extended.

In this assignment, it was possible to produce/edit a working artifact by carefully following tool output—or even by delegating much of the work to AI tools—without deeply understanding the pipeline itself. It was also possible to build substantial understanding without fully completing the artifact.

Write an essay engaging with Naur's argument and your own experience. You do not need to answer every question below, but your essay should substantively engage with **the tension between theory-building and tool-driven development**.

You may consider:

* **Your experience**: To what extent did you build a theory of the codebase? What could you now do with it—extend it, debug it, explain it to someone else? If you did not build a full theory, what *did* you build instead?

* **The role of tools**: Did the linter, type checker, auto-fixes, Makefile, or shell scripts help you build theory, or did they make theory-building unnecessary? Is there a meaningful difference between understanding *why* a rule exists and merely satisfying it?

* **AI and theory**: If you used AI tools, did they accelerate theory-building, replace it, or obscure it? Were there moments where AI outputs were plausible but wrong, and how did you detect or reason about that?

* **Implications**: If code can be modified or improved without building a theory of it, what does that imply for maintenance, collaboration, and onboarding? Is Naur's concern outdated—or more relevant than ever?

A thoughtful defense of either theory-free or tool-driven programming is **entirely acceptable** if it is well reasoned and grounded in your experience.

---

## Submission

The written reflection is submitted separately from your artifact:

1. Write your responses in this document (or a copy of it, in any editor you like).
2. Upload the completed `WRITTEN.md` to the **HW1 Written** assignment on Gradescope.

### Formatting Guidelines

- **For all parts:** Aim for and prioritize clarity and honest engagement
- **Parts 1–3**: ~1–2 paragraphs each
- **Part 4**: **~500–700 words** (roughly one single-spaced page) - it's acceptable to be slightly over
