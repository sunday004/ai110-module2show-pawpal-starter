# PawPal+ Project Reflection

## 1. System Design

Core user actions for PawPal+:

- The user can enter and update basic owner and pet information so the planner understands who the schedule is for.
- The user can add and edit pet care tasks, including at least duration and priority, so each task has clear scheduling inputs.
- The user can generate and view a daily care plan that reflects constraints and priorities, along with a clear explanation of why tasks were ordered that way.

**a. Initial design**

My initial UML design used four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- `Owner` holds owner-specific planning inputs (daily time available, preferred task order, reminder settings).
- `Pet` stores pet profile details that affect care planning (species, age, energy level, and special needs).
- `Task` represents individual care activities (walk, feeding, meds, enrichment) with duration, priority, and timing metadata.
- `Scheduler` is responsible for ranking tasks, resolving conflicts, building the daily plan, and explaining scheduling choices.

This design separates data objects (`Pet`, `Task`) from coordination logic (`Scheduler`) so the planning behavior can evolve without overloading the UI layer.

**b. Design changes**

Yes. After reviewing `pawpal_system.py`, I made relationship-focused updates:

- I added an explicit `Owner -> Pet` relationship in code by giving `Owner` a `pets` collection and adding `add_pet()` / `remove_pet()` method stubs.
- I updated `Scheduler` so it takes `owner`, `pets`, and `task_list` in its constructor instead of only `task_list`.

I made these changes to reduce hidden coupling and avoid a future bottleneck where scheduling logic would need owner preferences and pet context but not receive them directly. This keeps dependencies explicit and makes the system easier to test.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers due date/time, priority score, completion status, and the owner's daily available minutes.
I prioritized these constraints because they directly affect whether a task is urgent and realistically achievable in a single day.
The ranking logic favors incomplete tasks first, then higher priority, then earlier due times, and finally shorter duration as a tie-breaker.

**b. Tradeoffs**

One tradeoff is that conflict detection currently checks only exact same due timestamps instead of full duration overlap windows.
This is reasonable for the current PawPal+ scope because it keeps the algorithm simple, transparent, and fast for small daily task lists, while still catching the most obvious scheduling collisions that matter to a busy owner.

---

## 3. AI Collaboration

**a. How you used AI**

I used Copilot Chat for class design brainstorming, method naming, and implementation sequencing.
I used inline assistance to speed up repetitive code tasks like docstrings and test skeleton generation.
The most helpful prompts were concrete and scoped, such as "add filtering by pet and completion status" and "design a lightweight conflict warning method."
Using separate chat sessions by phase (design, implementation, testing, polish) helped me keep requirements isolated and reduced context mixing when making decisions.

**b. Judgment and verification**

I rejected a more complex conflict-resolution approach that tried to optimize overlapping durations with extra state tracking because it reduced readability for this project scope.
I kept exact-time conflict warnings instead and verified correctness by creating same-time tasks in the CLI demo and by adding an automated conflict-detection pytest case.

---

## 4. Testing and Verification

**a. What you tested**

I ran: python -m pytest

I tested task completion state changes, adding tasks to pets, chronological sorting, recurring task creation after completion, filtering correctness, and conflict warning detection.
These tests were important because they validate both basic class behavior and the algorithmic features that make the scheduler useful.

**b. Confidence**

My confidence level is 4/5 based on repeatable demo outputs and passing automated tests.
With more time, I would test overlapping-duration conflicts (not just exact timestamps), timezone behavior, very large task sets, and mixed recurrence rules across multiple weeks.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the clean separation between data models (`Owner`, `Pet`, `Task`) and the decision layer (`Scheduler`), which made iteration and testing straightforward.

**b. What you would improve**

In another iteration, I would add persistent storage (JSON/CSV), richer overlap-aware conflict detection, and stronger UI controls for marking tasks complete and viewing recurring history.

**c. Key takeaway**

My key takeaway is that AI is most effective when I stay the lead architect: define constraints first, ask focused questions, verify outputs with tests, and accept only suggestions that improve both correctness and maintainability.
