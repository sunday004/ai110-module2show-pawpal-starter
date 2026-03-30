from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
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

	def to_dict(self) -> dict[str, Any]:
		"""Serialize owner state, pets, and tasks to a plain dictionary."""
		return {
			"owner_name": self.owner_name,
			"available_minutes_per_day": self.available_minutes_per_day,
			"preferred_task_order": self.preferred_task_order,
			"medication_reminder_enabled": self.medication_reminder_enabled,
			"pets": [pet.to_dict() for pet in self.pets],
		}

	def save_to_json(self, file_path: str = "data.json") -> None:
		"""Save owner, pets, and tasks to JSON for persistence between runs."""
		if not file_path.strip():
			raise ValueError("file_path cannot be empty.")

		path = Path(file_path)
		if path.parent and str(path.parent) != ".":
			path.parent.mkdir(parents=True, exist_ok=True)

		with path.open("w", encoding="utf-8") as outfile:
			json.dump(self.to_dict(), outfile, indent=2)

	@classmethod
	def load_from_json(cls, file_path: str = "data.json") -> Owner:
		"""Load owner, pets, and tasks from a JSON file."""
		path = Path(file_path)
		if not path.exists():
			raise FileNotFoundError(f"Data file not found: {file_path}")

		with path.open("r", encoding="utf-8") as infile:
			payload = json.load(infile)

		required = {
			"owner_name",
			"available_minutes_per_day",
			"preferred_task_order",
			"medication_reminder_enabled",
			"pets",
		}
		missing = [key for key in required if key not in payload]
		if missing:
			raise ValueError(f"Missing required owner fields: {', '.join(missing)}")

		owner = cls(
			owner_name=str(payload["owner_name"]),
			available_minutes_per_day=int(payload["available_minutes_per_day"]),
			preferred_task_order=list(payload["preferred_task_order"]),
			medication_reminder_enabled=bool(payload["medication_reminder_enabled"]),
		)

		for pet_payload in payload.get("pets", []):
			owner.add_pet(Pet.from_dict(pet_payload))

		return owner


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
			if task.description == description and not task.completed:
				task.mark_completed()
				next_task = task.next_occurrence()
				if next_task is not None:
					self.add_task(next_task)
				return True
		return False

	def get_due_tasks(self, target_date: date) -> list[Task]:
		"""Return this pet's incomplete tasks due on the target date."""
		return [
			task
			for task in self.tasks
			if task.is_due_today(target_date) and not task.completed
		]

	def to_dict(self) -> dict[str, Any]:
		"""Serialize pet fields and all attached tasks to dictionary form."""
		return {
			"pet_name": self.pet_name,
			"species": self.species,
			"age": self.age,
			"energy_level": self.energy_level,
			"special_needs": self.special_needs,
			"tasks": [task.to_dict() for task in self.tasks],
		}

	@classmethod
	def from_dict(cls, payload: dict[str, Any]) -> Pet:
		"""Rebuild a pet instance from dictionary payload."""
		required = {"pet_name", "species", "age", "energy_level", "special_needs", "tasks"}
		missing = [key for key in required if key not in payload]
		if missing:
			raise ValueError(f"Missing required pet fields: {', '.join(missing)}")

		pet = cls(
			pet_name=str(payload["pet_name"]),
			species=str(payload["species"]),
			age=int(payload["age"]),
			energy_level=str(payload["energy_level"]),
			special_needs=str(payload["special_needs"]),
		)

		for task_payload in payload.get("tasks", []):
			pet.add_task(Task.from_dict(task_payload))

		return pet


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

	def next_occurrence(self) -> Task | None:
		"""Create the next scheduled instance for daily or weekly tasks."""
		frequency = self.frequency.strip().lower()
		if frequency == "daily":
			next_due = self.due_at + timedelta(days=1)
		elif frequency == "weekly":
			next_due = self.due_at + timedelta(days=7)
		else:
			return None

		return Task(
			description=self.description,
			due_at=next_due,
			frequency=self.frequency,
			completed=False,
			priority=self.priority,
			duration_minutes=self.duration_minutes,
			category=self.category,
			notes=self.notes,
			pet_name=self.pet_name,
		)

	def to_dict(self) -> dict[str, Any]:
		"""Serialize task including due datetime in ISO-8601 format."""
		return {
			"description": self.description,
			"due_at": self.due_at.isoformat(),
			"frequency": self.frequency,
			"completed": self.completed,
			"priority": self.priority,
			"duration_minutes": self.duration_minutes,
			"category": self.category,
			"notes": self.notes,
			"pet_name": self.pet_name,
		}

	@classmethod
	def from_dict(cls, payload: dict[str, Any]) -> Task:
		"""Rebuild a task instance from a dictionary payload."""
		required = {
			"description",
			"due_at",
			"frequency",
			"completed",
			"priority",
			"duration_minutes",
			"category",
			"notes",
			"pet_name",
		}
		missing = [key for key in required if key not in payload]
		if missing:
			raise ValueError(f"Missing required task fields: {', '.join(missing)}")

		try:
			due_at = datetime.fromisoformat(str(payload["due_at"]))
		except ValueError as exc:
			raise ValueError(f"Invalid task due_at datetime: {payload['due_at']}") from exc

		return cls(
			description=str(payload["description"]),
			due_at=due_at,
			frequency=str(payload["frequency"]),
			completed=bool(payload["completed"]),
			priority=int(payload["priority"]),
			duration_minutes=int(payload["duration_minutes"]),
			category=str(payload["category"]),
			notes=str(payload["notes"]),
			pet_name=str(payload["pet_name"]) if payload["pet_name"] is not None else None,
		)


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

	def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
		"""Sort tasks by due datetime in ascending order."""
		items = tasks if tasks is not None else self.refresh_task_cache()
		return sorted(items, key=lambda task: task.due_at)

	def filter_tasks(
		self,
		pet_name: str | None = None,
		completed: bool | None = None,
		target_date: date | None = None,
	) -> list[Task]:
		"""Filter tasks by pet name, completion status, and/or due date."""
		tasks = self.refresh_task_cache()

		if pet_name is not None:
			tasks = [task for task in tasks if task.pet_name == pet_name]
		if completed is not None:
			tasks = [task for task in tasks if task.completed == completed]
		if target_date is not None:
			tasks = [task for task in tasks if task.is_due_today(target_date)]

		return tasks

	def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
		"""Return readable warnings for tasks sharing the same due time."""
		items = self.sort_by_time(tasks if tasks is not None else self.refresh_task_cache())
		warnings: list[str] = []
		tasks_by_due: dict[datetime, list[Task]] = {}

		for task in items:
			tasks_by_due.setdefault(task.due_at, []).append(task)

		for due_at, group in tasks_by_due.items():
			if len(group) < 2:
				continue
			pet_names = sorted({task.pet_name or "unknown" for task in group})
			descriptions = ", ".join(task.description for task in group)
			warnings.append(
				f"Conflict at {due_at.strftime('%Y-%m-%d %H:%M')}: "
				f"{descriptions} (pets: {', '.join(pet_names)})"
			)

		return warnings

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

	def find_next_available_slot(
		self,
		duration_minutes: int,
		start_from_date: date,
		day_start_hour: int = 6,
		day_end_hour: int = 22,
	) -> datetime | None:
		"""Find the earliest available slot on a date for the requested duration."""
		if duration_minutes <= 0:
			raise ValueError("duration_minutes must be greater than zero.")

		tasks_for_day = self.sort_by_time(self.get_tasks_for_date(start_from_date))
		day_start = datetime.combine(start_from_date, datetime.min.time()).replace(hour=day_start_hour)
		day_end = datetime.combine(start_from_date, datetime.min.time()).replace(hour=day_end_hour)

		if day_start >= day_end:
			raise ValueError("day_start_hour must be earlier than day_end_hour.")

		required_delta = timedelta(minutes=duration_minutes)
		cursor = day_start

		if not tasks_for_day:
			if cursor + required_delta <= day_end:
				return cursor
			return None

		for task in tasks_for_day:
			task_start = task.due_at
			task_end = task_start + timedelta(minutes=task.duration_minutes)

			if task_start - cursor >= required_delta:
				return cursor

			if task_end > cursor:
				cursor = task_end

		if day_end - cursor >= required_delta:
			return cursor

		return None
