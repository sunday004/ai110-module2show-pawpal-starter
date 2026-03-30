from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


class Owner:
	"""Represents the pet owner profile and planning preferences."""

	def __init__(
		self,
		owner_name: str,
		available_minutes_per_day: int,
		preferred_task_order: list[str],
		medication_reminder_enabled: bool,
	) -> None:
		self.owner_name = owner_name
		self.available_minutes_per_day = available_minutes_per_day
		self.preferred_task_order = preferred_task_order or []
		self.medication_reminder_enabled = medication_reminder_enabled
		self.pets: list[Pet] = []

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner, enforcing unique pet names."""
		if any(existing.pet_name == pet.pet_name for existing in self.pets):
			raise ValueError(f"Pet '{pet.pet_name}' already exists for this owner.")
		self.pets.append(pet)

	def remove_pet(self, pet_name: str) -> None:
		"""Remove a pet by name if it exists."""
		self.pets = [pet for pet in self.pets if pet.pet_name != pet_name]

	def update_preferences(self, preferences: dict[str, Any]) -> None:
		"""Update owner scheduling preferences from a partial dictionary."""
		if "preferred_task_order" in preferences:
			self.preferred_task_order = list(preferences["preferred_task_order"])
		if "medication_reminder_enabled" in preferences:
			self.medication_reminder_enabled = bool(preferences["medication_reminder_enabled"])

	def set_daily_availability(self, minutes: int) -> None:
		"""Set the owner's daily available planning minutes."""
		if minutes <= 0:
			raise ValueError("Daily availability must be greater than 0 minutes.")
		self.available_minutes_per_day = minutes

	def get_profile_summary(self) -> str:
		"""Return a compact summary of owner planning context."""
		return (
			f"Owner: {self.owner_name} | "
			f"Daily availability: {self.available_minutes_per_day} min | "
			f"Pets: {len(self.pets)}"
		)

	def get_all_tasks(self, include_completed: bool = True) -> list[Task]:
		"""Return tasks across all pets for dashboard and scheduling usage."""
		all_tasks: list[Task] = []
		for pet in self.pets:
			all_tasks.extend(pet.list_tasks(include_completed=include_completed))
		return all_tasks

	def get_all_due_tasks(self, target_date: date) -> list[Task]:
		"""Collect all incomplete tasks due on a given date across pets."""
		due_tasks: list[Task] = []
		for pet in self.pets:
			due_tasks.extend(pet.get_due_tasks(target_date))
		return due_tasks


@dataclass
class Pet:
	"""Stores pet details used by the scheduler."""

	pet_name: str
	species: str
	age: int
	energy_level: str
	special_needs: str
	tasks: list[Task] = field(default_factory=list)

	def update_pet_info(self, info: dict[str, Any]) -> None:
		"""Apply partial pet profile updates for known fields."""
		for key, value in info.items():
			if hasattr(self, key):
				setattr(self, key, value)

	def get_care_needs(self) -> str:
		"""Return the pet's special needs text or a default message."""
		if self.special_needs.strip():
			return self.special_needs
		return "No special care needs recorded."

	def get_pet_summary(self) -> str:
		"""Return a compact summary of this pet and its task load."""
		return (
			f"{self.pet_name} ({self.species}, age {self.age}) | "
			f"Energy: {self.energy_level} | Tasks: {len(self.tasks)}"
		)

	def add_task(self, task: Task) -> None:
		"""Attach a task to this pet and set pet_name when missing."""
		if task.pet_name is None:
			task.pet_name = self.pet_name
		self.tasks.append(task)

	def remove_task(self, description: str) -> None:
		"""Remove tasks matching the provided description."""
		self.tasks = [task for task in self.tasks if task.description != description]

	def list_tasks(self, include_completed: bool = True) -> list[Task]:
		"""List this pet's tasks, optionally excluding completed ones."""
		if include_completed:
			return list(self.tasks)
		return [task for task in self.tasks if not task.completed]

	def mark_task_completed(self, description: str) -> bool:
		"""Mark the first matching task as completed and report success."""
		for task in self.tasks:
			if task.description == description:
				task.mark_completed()
				return True
		return False

	def get_due_tasks(self, target_date: date) -> list[Task]:
		"""Return this pet's incomplete tasks due on the target date."""
		return [
			task
			for task in self.tasks
			if task.is_due_today(target_date) and not task.completed
		]


@dataclass
class Task:
	"""Represents a single care task that can be scheduled."""

	description: str
	due_at: datetime
	frequency: str
	completed: bool = False
	priority: int = 2
	duration_minutes: int = 15
	category: str = "general"
	notes: str = ""
	pet_name: str | None = None

	def edit_task(self, details: dict[str, Any]) -> None:
		"""Update editable task fields from a dictionary."""
		for key, value in details.items():
			if hasattr(self, key):
				setattr(self, key, value)
			else:
				raise KeyError(f"Unknown task field: {key}")

	def is_due_today(self, target_date: date) -> bool:
		"""Return True when the task due date matches the target date."""
		return self.due_at.date() == target_date

	def mark_completed(self) -> None:
		"""Mark this task as completed."""
		self.completed = True

	def mark_complete(self) -> None:
		"""Compatibility alias for simpler external calls/tests."""
		self.mark_completed()

	def estimate_urgency_score(self) -> float:
		"""Estimate urgency from priority, due time, and completion state."""
		now = datetime.now()
		hours_to_due = (self.due_at - now).total_seconds() / 3600
		if hours_to_due <= 0:
			time_score = 2.0
		else:
			time_score = max(0.1, 24.0 / (hours_to_due + 1))
		completion_penalty = -100.0 if self.completed else 0.0
		return (self.priority * 10.0) + time_score + completion_penalty


class Scheduler:
	"""Builds and explains a daily task plan."""

	def __init__(
		self,
		owner: Owner,
		pets: list[Pet] | None = None,
		task_list: list[Task] | None = None,
	) -> None:
		self.owner = owner
		self.pets = pets if pets is not None else owner.pets
		self.task_list = task_list if task_list is not None else owner.get_all_tasks()
		self._last_explanation = "No plan generated yet."

	def refresh_task_cache(self) -> list[Task]:
		"""Refresh and return cached tasks from all managed pets."""
		self.task_list = []
		for pet in self.pets:
			self.task_list.extend(pet.tasks)
		return self.task_list

	def get_tasks_for_date(self, target_date: date) -> list[Task]:
		"""Get all tasks scheduled for a specific date across pets."""
		self.refresh_task_cache()
		return [task for task in self.task_list if task.is_due_today(target_date)]

	def rank_tasks(self, tasks: list[Task]) -> list[Task]:
		"""Sort tasks by completion, priority, due time, and duration."""
		return sorted(
			tasks,
			key=lambda task: (
				task.completed,
				-task.priority,
				task.due_at,
				task.duration_minutes,
			),
		)

	def build_daily_plan(self, target_date: date) -> list[Task]:
		"""Build a date-specific plan constrained by owner time budget."""
		tasks_for_day = [task for task in self.get_tasks_for_date(target_date) if not task.completed]
		ranked = self.rank_tasks(tasks_for_day)

		selected: list[Task] = []
		used_minutes = 0
		for task in ranked:
			if used_minutes + task.duration_minutes <= self.owner.available_minutes_per_day:
				selected.append(task)
				used_minutes += task.duration_minutes

		self._last_explanation = (
			f"Selected {len(selected)} of {len(ranked)} tasks for {target_date.isoformat()} "
			f"within {self.owner.available_minutes_per_day} available minutes."
		)
		return selected

	def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
		"""Resolve same-slot pet task conflicts by keeping higher priority."""
		# Keep only one task for each pet+time slot, preferring higher-priority tasks.
		sorted_by_priority = sorted(tasks, key=lambda task: task.priority, reverse=True)
		seen_slots: set[tuple[str, datetime]] = set()
		resolved: list[Task] = []

		for task in sorted_by_priority:
			slot = (task.pet_name or "unknown", task.due_at)
			if slot in seen_slots:
				continue
			seen_slots.add(slot)
			resolved.append(task)

		return sorted(resolved, key=lambda task: task.due_at)

	def explain_selection_logic(self) -> str:
		"""Return a human-readable summary of the latest planning decision."""
		return self._last_explanation
