from datetime import datetime, timedelta

from pawpal_system import Pet, Task


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
