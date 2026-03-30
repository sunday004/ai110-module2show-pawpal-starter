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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
