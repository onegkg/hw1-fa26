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
| 1. Lint errors fixed (`ruff check` passes) | done | |
| 2. Type annotations added (`mypy` passes) | done | had to ignore type errors on textblob because I couldn't find any typed stubs |
| 3. Shell script fixed (`shellcheck` passes) | done | |
| 4. Makefile wires `RUN_TAG` and `SCHEMA_VERSION` correctly | done | |
| 5. Contract mismatch resolved (`make run-all` passes) | done | moved from percentage to decimal |
| 6. Contracts enforced at every boundary (`tests/test_boundaries.py` passes) | done | added a validation step to `make plot` and made some changes to the validation functions |
| 7. All CI jobs pass | done | |
| 8. Local evidence screenshot included | done | |

### Understanding Self-Check

Answer briefly (1–3 sentences each):

1. **What do you feel you genuinely understand** about this assignment? (Not just "made it work," but could explain to someone else or extend on your own.)
    - How makefiles work (not one hundred percent with the syntax yet, but I generally understand the semantics)
    - The pros and cons of type checkers in dynamically typed languages

2. **What did you make work without fully understanding?** (Be honest—this is valuable self-knowledge.)
    - Wiring the parameters through the makefile, while i mostly understood what was going on, I felt the comments in the makefile allowed me to make the updates without as much understanding as I would have liked to have
    - Schema v2; The plot function didn't handle the `support` dictionary by default and I wasn't sure what to do with it, so I just excluded the info from the final graph

3. **Where did you get stuck?** What did you try before moving on or seeking help?
    - I had some environment issues (this was primarily my fault for wanting to use neovim) but I was able to resolve them on my own with the help of claude, the UV documentation, and a couple of reddit/stackoverflow posts on using devcontainers with cli environments. I ended up just booting the raw docker image in a seperate terminal tab and switching over to it when I needed to run tests
    - I got stuck for a while trying to figure out how to get mypy to recognize the `textblob` types before I realized they didn't exist and if I wanted types for textblob I would have to write the stubs myself. The troubleshooting for this consisted of using claude, the mypy documentation, and the pypi page for textblob.


---

## Part 1: Short Response (1 paragraph each)

### A: Your Path Through the Assignment

Briefly describe how you approached this assignment. Did you try to build a mental model of how the pipeline worked before fixing it? Did you focus primarily on satisfying tools like `ruff`, `mypy`, or the Makefile? Did your approach change over time?

There is no wrong answer—be honest about what you actually did, not what you think you *should* have done.

In the early stages of the assignment I focused almost exclusively on satisfying the linters and typecheckers, only understanding enough context to add the correct type annotations. As i worked through later stages of the project. I had to get a better sense of the project, but still only understood as much as I felt I needed to solve the problem at hand. This resulted in me having a pretty decent understanding of the contracts at the borders of each module, but having a rather poor understanding of the internals of the modules, or even what they do.

### B: Friction and Flow

Which parts of this assignment felt like *productive friction* (friction that forced you to learn something valuable), and which felt like *unproductive friction* (busywork, confusion, or tool pain that didn't help)? Be specific about where those moments occurred.

Adding type annotations definitely felt like productive friction. It forced me to dive in to the implementation, and learn (a little bit) about how each function works, or at least how the contracts at the borders of each function work. The linters felt much less productive. Linters generally enforce non-specific code style guidelines, which didn't teach me anything about the codebase, it just gave me a bunch of things to fix (especially since ruff for whatever reason wanted to transform the `%` formatting syntax into `"literal".format()` instead of an fstring, so I had to make those updates by hand). I felt that the Makefile portion was a little bit too guided, which prevented me from needing to learn about the codebase or the details of the makefile. The final portion in which we had to fix the schema mismatch felt very productive to me. I liked that it was not straightforward and had more nuance, and emulated a real bug that might happen in production.

### C: Automation Tools

Which automated fixes did you apply, and which did you review, undo, or decline? How did you decide which ones to trust?

If you used LLM-powered tools, what did you use them for? What did they do well? Where did they fail, mislead you, or require careful verification? If you instead chose to do everything by hand, where do you wish automation would have helped?

I applied all of the safe `ruff` fixes, but manually fixed the outdated formatting syntax, since `ruff` didn't auto-fix to modern fstring syntax. Shellcheck fixes I did entirely manually, using [compile-mode.nvim](https://github.com/ej-shafran/compile-mode.nvim) to jump to the point of the error and fix it. I chose to do it this way because it was easier to vet this way than by previewing the git diff and most of the fixes were pretty simple to resolve.

I used LLMs in this project as basically a glorified stackoverflow. I asked them questions that I didn't feel were likely to be included in the documentation for whatever tool I was questioning or to confirm that my understanding of a tool was correct.

---

## Part 2: Course Connections (1–2 paragraphs each)

### A: Designs for Compliance (Franklin)

In the assigned pages, Franklin walks through how a Shang Dynasty foundry cast a bronze vessel, including the different roles of the designer and model builder and of the potter who made the molds. Look back at what she says each of those roles needed to know, and how much room each had for their own judgement.

Where in this assignment did you work like the potter, and where, if anywhere, did you work like the model builder? Who laid down the prescriptions you followed, and who benefits from software work being organized this way?

In the assigned pages, presents the designers and model builders as overseer type roles. They may not be working in a fully holistic model, since they are passing over control of the work in the later steps, but they must design the models with those later steps in mind. In contrast, the potter who creates the molds, has a much more limited (though no less important) job: to make the mold. They don't need to know much about the rest of the process, they just need to look at the thing in front of them, and perform the necessary steps to create the mold.

For most of the assigment, I felt like the potter, taking the code in front of me and performing necessary transformations in order to produce a desired result (eg. passing lints/typechecks/unit tests). The only place where I felt more like a designer was in the the portion in which I was fixing the schema mismatch. This however, was a relative feeling of control, which was still on the prescriptive end of the spectrum (see the figure below). The prescriptions were laid out by a number of people: The designer of the assignment, the creators of `ruff`, `mypy`, and `shellcheck`, and the designer of the codebase all had a large say in how I needed to approach the assignment. The assignment designer is the most obvious orchestrator, as they have given me explicit instructions about what should be done. The creators of the static analysis tools, however, have perhaps a somewhat less obvious prescriptive role. While the tools present themselves as authoritative, someone wrote the linting rules, and that person (or group of people, more likely) had to make decisions about what is and is not "good style", which may or may not match with the personal preferences of individual users of the tools. The designer of the codebase also has a significant prescriptive role. They prescribed everything from the module layout to the flow between modules to the specific implementation details of individual functions. Since I am handing off the code to a test suite which expects many of these prescriptions to be true (and since I am tasked with fixing lints and resolving schema errors rather than refactoring the code), I am bound by these prescriptions. I would argue that almost everyone involved benefits from software development being organized this way. Individual developers are able to focus on solving a specific problem, without needing extensive knowledge about how code in other parts of the codebase works, Teams of developers can reasonably expect that they will not wake up one day to their abstractions having a totally new API, companies can create larger and more ambitious projects than a single developer could take on alone, and end users can expect better services from those companies.

```
    holistic                                                                                                    prescriptive
    <--------------------------------------------------------------------------------------------------------------->
                                                                          ^                         ^
                                                                       fixing schema mismatch       the rest of the assignment
```

### B: Abstractions as Contracts (Liskov)

Barbara Liskov presented the idea that components should interact through well-defined contracts—agreements about inputs, outputs, and behavior—rather than relying on implementation details. We've seen this pattern in multiple technologies so far, with abstraction layers adhering to contracts that simultaneously *enforce* constraints while *enabling* other capabilities (e.g., LLVM IR constraining the compiler target output while enabling portability).

Where did the contracts in this assignment (CLI flags, file formats, Makefile targets, validation steps) constrain you, and what did those constraints enable? Then consider the cost: is making every contract explicit and enforced always worth it? Describe a case, in this pipeline or elsewhere, where you would leave a contract implicit, and why.

A specific contract from the assignment that constrained me, but that I feel was nevertheless worth the constraint were the unit tests. They obviously limit the space of potential solutions, but without them, it would be nearly impossible to tell what was failing and where in parts 5 and 6.

To be honest, implicit contracts seem to me like generally a bad idea. The best case scenario when an implicit contract is violated is that you hit a bizarre error somewhere down the line, but perhaps equally likely is the possibility that you end up with undefined behaviour that at best gives you an incorrect result and at worst gives a segfault, corrupted memory, or even a security vulnerability. It seems like a better idea to force compliance as early as possible, and fail in an agreed upon way if they are violated. With that being said, plenty of real projects, especially in C and C++ rely on undefined behaviour, and would break if the contracts began being explicitly checked. So I guess in my mind the place for implicit contracts is in established systems where users rely on the contract to be implicit, but any new projects should attempt to be as explicit with their contracts as possible.

---

## Part 3: Resolving a Contract Mismatch (1–2 paragraphs)

In Task 5, two parts of the pipeline disagreed about what an artifact contains. Which side did you change, and what evidence led you there? Would you have chosen the same contract if the design were entirely up to you, and, given that the autograder accepts some resolutions but not others, how much of that decision was really yours to make?

In task 5, I updated the artifact schema to list the metrics as a float rather than a percentage. I made this decision since it seemed to be the format that the unit tests expected and was the format that the rest of the codebase used as well as the fact that the names of the fields did not indicate that they were percentages, which could lead to more confusion down the line. If I were designing the system myself, I likely would have gone with a schema that used percents (with a name that includes the fact that it is a percentage) stored as integers to avoid floating point arithmetic errors.

I would argue that even if the auto-grader was not present, I still would not have full creative freedom (at least if I wanted to not get yelled at by whoever I'm passing the code to down the line). There is a finite set of reasonable approaches to the problem, and that set gets narrowed by elements of the codebase that are outside of my control. I could theoretically change both sides of the pipeline to expect those fields to be a string, and even if the autograder doesn't get mad at me for that, my coworkers certainly would!

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

I don't feel that tool driven development and theory driven development are opposing methodologies, rather they are solutions to different but overlapping problems. Theory is essential for making architectural decisions (and decisions impacted by those architectural decisions). Tools do not get in the way of those architectural decisions, but rather ensure that the implementation details don't get in the way of the decisions.

In Peter Naur's *Programming as Theory Building*, he argues that Programming *is* the act of theory-building. Theory is built up through interaction with a codebase, and meaningful changes can only be made effectively by those possessing a theory of the codebase. Last semester I took Prof. Delfino's Software Engineering course which involved creating a large semesterlong project in collaboration with three others. Throughout the semester, each of us specialized in one or two well encapsulation portions of the codebase. We reviewed each other's PRs and so we each had a general sense of what was going on in other portions of the codebase, but the code changes in that portion of the codebase were made by that portion's specialists. There were a couple times throughout the semester where one team member would be otherwise occupied and would ask the rest of the group to fill in for them that week. These times made it clear to me how important theory is for making meaningful changes to a codebase. Despite the fact that I had interacted with the external APIs and reviewed the code from these portions almost every day for multiple months, I was still always lost. I struggled to make the changes we had already decided on. I can't imagine even attempting to make any sort of major architectural decisions in that context.

In part 7: *Method and Theory Building* Naur argues against the relative usefullness of "Methods" in comparison to his Theory Building View, limiting their usefulness to the onboarding process. He defines methods as "a set of work rules for the programmers, telling what kind of things the programmers should do, in what order, which notations or languages to use, and what kinds of documents to produce at various stages" (Naur, 259). This definition of methods brings linters to mind. After all, what is a linter if not a tool for enforcing a set of work rules on the programmer. Since I think linters are generally quite useful, Naur's dismissal of methods may seem puzzling at first. But upon further inspection, it becomes clear that Naur is not claiming that methods are entirely useless, rather he (perhaps implicitly) claims that they are not useful for making meaningful decisions about programs. Similarly linters are useful for catching mechanical errors, things like outdated idioms or failing to check for a null pointer, but they are not designed to, and in fact are not capable of, catching the sort of larger scale architectural issues that Naur is focused on. Similarly, while following programming methods may allow you to write cleaner or better documented or more idiomatic code, they do nothing to help the programmer when it comes to making the big, important decisions, that theory is so necessary for


## Submission

The written reflection is submitted separately from your artifact:

1. Write your responses in this document (or a copy of it, in any editor you like).
2. Upload the completed `WRITTEN.md` to the **HW1 Written** assignment on Gradescope.

### Formatting Guidelines

- **For all parts:** Aim for and prioritize clarity and honest engagement
- **Parts 1–3**: ~1–2 paragraphs each
- **Part 4**: **~500–700 words** (roughly one single-spaced page) - it's acceptable to be slightly over
