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
			description="Morning walk",
			due_at=datetime.combine(today, time(hour=8, minute=0)),
			frequency="daily",
			priority=3,
			duration_minutes=25,
			category="walk",
		)
	)
	dog.add_task(
		Task(
			description="Lunch feeding",
			due_at=datetime.combine(today, time(hour=12, minute=30)),
			frequency="daily",
			priority=2,
			duration_minutes=10,
			category="feeding",
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

	scheduler = Scheduler(owner=owner)
	return owner, scheduler


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
	today = datetime.now().date()
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
