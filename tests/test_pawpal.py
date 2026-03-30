from datetime import date, datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def _build_owner_with_two_pets() -> tuple[Owner, Pet, Pet]:
	owner = Owner(
		owner_name="Jordan",
		available_minutes_per_day=120,
		preferred_task_order=["meds", "feeding", "walk"],
		medication_reminder_enabled=True,
	)
	dog = Pet("Mochi", "dog", 4, "high", "")
	cat = Pet("Luna", "cat", 7, "medium", "")
	owner.add_pet(dog)
	owner.add_pet(cat)
	return owner, dog, cat


def test_task_completion_changes_status() -> None:
	"""Calling mark_complete should set completed status to True."""
	task = Task(
		description="Evening feeding",
		due_at=datetime.now() + timedelta(hours=2),
		frequency="daily",
	)

	assert task.completed is False
	task.mark_complete()
	assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
	"""Adding a task to a pet should increase that pet's task count."""
	pet = Pet(
		pet_name="Mochi",
		species="dog",
		age=4,
		energy_level="high",
		special_needs="",
	)
	task = Task(
		description="Morning walk",
		due_at=datetime.now() + timedelta(hours=1),
		frequency="daily",
	)

	starting_count = len(pet.tasks)
	pet.add_task(task)

	assert len(pet.tasks) == starting_count + 1


def test_sorting_returns_chronological_order() -> None:
	"""Scheduler.sort_by_time should order tasks from earliest to latest."""
	owner, dog, _ = _build_owner_with_two_pets()

	dog.add_task(
		Task(
			description="Noon walk",
			due_at=datetime(2026, 3, 30, 12, 0),
			frequency="daily",
		)
	)
	dog.add_task(
		Task(
			description="Morning feeding",
			due_at=datetime(2026, 3, 30, 8, 30),
			frequency="daily",
		)
	)
	dog.add_task(
		Task(
			description="Evening meds",
			due_at=datetime(2026, 3, 30, 18, 0),
			frequency="daily",
		)
	)

	scheduler = Scheduler(owner=owner)
	sorted_tasks = scheduler.sort_by_time()

	assert [task.description for task in sorted_tasks] == [
		"Morning feeding",
		"Noon walk",
		"Evening meds",
	]


def test_daily_recurrence_creates_next_day_task() -> None:
	"""Completing a daily task should spawn a new occurrence for next day."""
	_, dog, _ = _build_owner_with_two_pets()
	original_due = datetime(2026, 3, 30, 9, 0)
	daily_task = Task(
		description="Breakfast",
		due_at=original_due,
		frequency="daily",
	)
	dog.add_task(daily_task)

	completed = dog.mark_task_completed("Breakfast")

	assert completed is True
	assert len(dog.tasks) == 2
	new_instances = [task for task in dog.tasks if not task.completed and task.description == "Breakfast"]
	assert len(new_instances) == 1
	assert new_instances[0].due_at == original_due + timedelta(days=1)


def test_conflict_detection_flags_duplicate_due_times() -> None:
	"""Scheduler should return conflict warnings for same-time tasks."""
	owner, dog, cat = _build_owner_with_two_pets()
	due_time = datetime(2026, 3, 30, 12, 0)

	dog.add_task(Task(description="Dog walk", due_at=due_time, frequency="daily"))
	cat.add_task(Task(description="Cat feeding", due_at=due_time, frequency="daily"))

	scheduler = Scheduler(owner=owner)
	warnings = scheduler.detect_conflicts()

	assert len(warnings) == 1
	assert "Conflict at 2026-03-30 12:00" in warnings[0]
	assert "Dog walk" in warnings[0]
	assert "Cat feeding" in warnings[0]


def test_filter_by_pet_and_completion_status() -> None:
	"""Filtering should isolate incomplete tasks for one pet on a date."""
	owner, dog, cat = _build_owner_with_two_pets()
	target_date = date(2026, 3, 30)

	dog.add_task(
		Task(
			description="Dog breakfast",
			due_at=datetime(2026, 3, 30, 8, 0),
			frequency="daily",
		)
	)
	cat_task = Task(
		description="Cat breakfast",
		due_at=datetime(2026, 3, 30, 8, 15),
		frequency="daily",
	)
	cat_task.mark_complete()
	cat.add_task(cat_task)

	scheduler = Scheduler(owner=owner)
	filtered = scheduler.filter_tasks(pet_name="Mochi", completed=False, target_date=target_date)

	assert len(filtered) == 1
	assert filtered[0].description == "Dog breakfast"
