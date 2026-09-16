# HW1 Grading Rubric

This assignment is evaluated using **two independent letter grades**, as described in the syllabus:

* **Artifact & Automation Grade** – evaluates your technical work and engagement with automation tools
* **Written Reflection Grade** – evaluates your theory-building, reflection, and engagement with course ideas

These two grades measure *different learning outcomes*. They are not averaged mechanically, and strong performance in one does not automatically imply strong performance in the other.

**Important:** Early in the semester, this course places particular value on *engagement, reflection, and theory-building*. A strong written reflection can meaningfully offset incomplete technical execution on HW1. Later assignments will expect increasing strength in **both** areas.

---

## Part A: Artifact & Automation Grade

This grade evaluates how you engaged with the technical work of building, repairing, and automating the pipeline.

You are **not** graded solely on whether everything works. You *are* graded on whether your work shows good-faith effort, intentionality, and engagement with the automation tools.

### Artifact Grade: A+ / A / A-

You will receive an A-range artifact grade if **most** of the following are true:

* The pipeline largely works or is very close to working end-to-end
* The Makefile meaningfully orchestrates stages using dependencies (not just sequential commands)
* You seriously engaged with linting and type-checking, addressing most issues rather than disabling tools
* You showed judgment about when to review automated fixes: routine fixes can be trusted, while fixes that may change behavior were examined, reverted, or declined
* Contract checks between pipeline stages actually enforce the documented contracts, rather than merely running
* Required features were attempted thoughtfully, even if imperfectly

This grade reflects **strong control over the automation structure**, even if minor bugs or gaps remain.

---

### Artifact Grade: B+ / B / B-

You will receive a B-range artifact grade if:

* Significant portions of the pipeline work, but others are incomplete or brittle
* Automation structure is present but may rely on workarounds or overly sequential Make targets
* Linting and type-checking were partially addressed, with some unresolved issues, or automated fixes were applied wholesale without regard to what they changed
* Contract checks exist but leave gaps in what they enforce
* Core requirements were engaged with, but execution is uneven

This grade reflects **substantial progress**, but with clear room for improvement.

---

### Artifact Grade: C+ / C

You will receive a C-range artifact grade if:

* There is clear evidence of effort and engagement with the assignment
* Some pipeline stages or automation pieces work, but others do not
* The Makefile exists but provides limited orchestration or abstraction
* Linting/type-checking may largely fail, but were not ignored or bypassed

This grade reflects a **good-faith attempt** that did not fully succeed technically.

---

### Artifact Grade: D / E

You will receive a D or E if:

* There is little evidence of engagement with the technical work
* Automation tools were bypassed, disabled, or removed
* Minimal or superficial changes were made
* The submission does not reflect a serious attempt to complete the assignment

---

## Part B: Written Reflection Grade

This grade evaluates the quality of your reflection, theory-building, and engagement with course readings and ideas.

The written component is not a summary or justification—it is an opportunity to demonstrate *how you understand what you worked on*, including confusion, failure, or disagreement.

---

### Reflection Grade: A+ / A / A-

You will receive an A-range reflection grade if:

* Your writing is specific, honest, and grounded in your actual experience
* You engage deeply with Peter Naur’s idea of programming as theory-building
* Frameworks from course readings are used analytically, not just mentioned
* You reason carefully about contracts: what a contract should be, who gets to decide, and when enforcing it is worth the cost, using your own work as evidence
* You clearly articulate what you understand, what you don’t, and why
* If you used AI tools, you critically examine their role and limitations

This grade reflects **strong theory-building** or a well-defended critique of its necessity.

---

### Reflection Grade: B+ / B / B-

You will receive a B-range reflection grade if:

* Your reflection is thoughtful and accurate, but limited in depth or synthesis
* Course ideas are correctly described but not fully integrated into an argument
* Examples from your work are present but underdeveloped

This grade reflects **solid understanding**, with room to go deeper.

---

### Reflection Grade: C+ / C

You will receive a C-range reflection grade if:

* Your reflection is honest but vague or shallow
* You acknowledge confusion or partial understanding without fully unpacking it
* Course ideas are referenced but weakly connected to your experience

This grade reflects **partial theory-building** and awareness of learning gaps.

---

### Reflection Grade: D / E

You will receive a D or E if:

* The reflection is generic, boilerplate, or disconnected from the assignment
* There is little evidence of genuine engagement or understanding
* AI use (if any) is hidden or uncritically accepted

---

## How to Interpret the Two Grades

You will receive **two separate letter grades** for HW1: one for the artifact and one for the written reflection.

Examples:

* **Artifact: C+, Reflection: A** → strong understanding despite incomplete execution (acceptable for HW1)
* **Artifact: A-, Reflection: C** → working code but shallow engagement
* **Artifact: B, Reflection: B+** → solid performance across both dimensions

Both grades matter. HW1 is intentionally generous to reward engagement and theory-building; later assignments will place increasing emphasis on technical execution.

---

## Final Note

The goal of this assignment is not just to produce working code, but to understand **what it means to automate software work**—what knowledge gets encoded in tools, what gets hidden, and what remains the responsibility of the programmer.
