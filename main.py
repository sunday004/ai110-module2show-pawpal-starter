from __future__ import annotations

from datetime import datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_data() -> tuple[Owner, Scheduler]:
	"""Create sample owner, pets, and tasks for a terminal demo."""
	owner = Owner(
		owner_name="Jordan",
		available_minutes_per_day=90,
		preferred_task_order=["meds", "feeding", "walk", "enrichment"],
		medication_reminder_enabled=True,
	)

	dog = Pet(
		pet_name="Mochi",
		species="dog",
		age=4,
		energy_level="high",
		special_needs="Needs a midday walk.",
	)
	cat = Pet(
		pet_name="Luna",
		species="cat",
		age=7,
		energy_level="medium",
		special_needs="Daily medication with dinner.",
	)

	owner.add_pet(dog)
	owner.add_pet(cat)

	today = datetime.now().date()

	dog.add_task(
		Task(
			description="Lunch walk",
			due_at=datetime.combine(today, time(hour=12, minute=0)),
			frequency="daily",
			priority=3,
			duration_minutes=25,
			category="walk",
		)
	)
	dog.add_task(
		Task(
			description="Morning feeding",
			due_at=datetime.combine(today, time(hour=8, minute=30)),
			frequency="daily",
			priority=2,
			duration_minutes=10,
			category="feeding",
		)
	)
	dog.add_task(
		Task(
			description="Noon enrichment",
			due_at=datetime.combine(today, time(hour=12, minute=0)),
			frequency="weekly",
			priority=1,
			duration_minutes=20,
			category="enrichment",
		)
	)
	cat.add_task(
		Task(
			description="Evening medication",
			due_at=datetime.combine(today, time(hour=18, minute=30)),
			frequency="daily",
			priority=3,
			duration_minutes=5,
			category="meds",
		)
	)
	cat.add_task(
		Task(
			description="Noon feeding",
			due_at=datetime.combine(today, time(hour=12, minute=0)),
			frequency="daily",
			priority=3,
			duration_minutes=10,
			category="feeding",
		)
	)

	scheduler = Scheduler(owner=owner)
	return owner, scheduler


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
	today = datetime.now().date()

	print("\n=== All Tasks (Unsorted Input Order) ===")
	for task in owner.get_all_tasks():
		print(f"[{task.pet_name}] {task.description} at {task.due_at.strftime('%H:%M')}")

	print("\n=== Sorted By Time ===")
	for task in scheduler.sort_by_time():
		print(f"[{task.pet_name}] {task.description} at {task.due_at.strftime('%H:%M')}")

	print("\n=== Filter: Incomplete Tasks For Mochi ===")
	for task in scheduler.filter_tasks(pet_name="Mochi", completed=False, target_date=today):
		print(f"[{task.pet_name}] {task.description} at {task.due_at.strftime('%H:%M')}")

	conflict_warnings = scheduler.detect_conflicts()
	if conflict_warnings:
		print("\n=== Conflict Warnings ===")
		for warning in conflict_warnings:
			print(f"- {warning}")

	# Demonstrate recurring task behavior.
	mochi = next((pet for pet in owner.pets if pet.pet_name == "Mochi"), None)
	if mochi is not None:
		mochi.mark_task_completed("Morning feeding")
		recurring_candidates = [task for task in mochi.tasks if task.description == "Morning feeding" and not task.completed]
		if recurring_candidates:
			next_due = min(task.due_at for task in recurring_candidates)
			print(
				"\nRecurring task created: "
				f"Morning feeding rescheduled for {next_due.strftime('%Y-%m-%d %H:%M')}"
			)

	plan = scheduler.build_daily_plan(today)

	print("\\n=== PawPal+ Today's Schedule ===")
	print(owner.get_profile_summary())
	print(f"Date: {today.isoformat()}\\n")

	if not plan:
		print("No tasks scheduled for today.")
		return

	for idx, task in enumerate(plan, start=1):
		due_time = task.due_at.strftime("%I:%M %p")
		print(
			f"{idx}. [{task.pet_name}] {task.description} "
			f"at {due_time} | priority {task.priority} | {task.duration_minutes} min"
		)

	print("\\n" + scheduler.explain_selection_logic())


if __name__ == "__main__":
	owner_obj, scheduler_obj = build_demo_data()
	print_todays_schedule(owner_obj, scheduler_obj)
