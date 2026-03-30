# PawPal+ Project Reflection

## 1. System Design

Core user actions for PawPal+:

- The user can enter and update basic owner and pet information so the planner understands who the schedule is for.
- The user can add and edit pet care tasks, including at least duration and priority, so each task has clear scheduling inputs.
- The user can generate and view a daily care plan that reflects constraints and priorities, along with a clear explanation of why tasks were ordered that way.

**a. Initial design**

Step 2: List the building blocks

- `OwnerProfile`
	Attributes: owner_name, available_minutes_per_day, preferred_task_order, medication_reminder_preference.
	Methods: update_preferences(), set_daily_availability(), summarize_preferences().

- `PetProfile`
	Attributes: pet_name, species, age, energy_level, special_needs.
	Methods: update_pet_info(), get_care_needs(), summarize_pet().

- `CareTask`
	Attributes: task_name, category, duration_minutes, priority, due_window, frequency, notes.
	Methods: edit_task(), mark_completed(), is_due_today(), estimate_urgency_score().

- `DailyConstraints`
	Attributes: date, total_available_minutes, blocked_time_windows, max_tasks, owner_preferences.
	Methods: can_fit_task(), remaining_time(), apply_preference_rules().

- `Scheduler`
	Attributes: task_list, constraints, scoring_weights.
	Methods: rank_tasks(), build_daily_plan(), resolve_conflicts(), explain_selection_logic().

- `DailyPlan`
	Attributes: date, scheduled_tasks, unscheduled_tasks, total_scheduled_minutes, explanation.
	Methods: add_scheduled_task(), remove_task(), generate_summary(), to_display_rows().

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
