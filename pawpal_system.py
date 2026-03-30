from __future__ import annotations

from dataclasses import dataclass
from datetime import date
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
		self.preferred_task_order = preferred_task_order
		self.medication_reminder_enabled = medication_reminder_enabled

	def update_preferences(self, preferences: dict[str, Any]) -> None:
		pass

	def set_daily_availability(self, minutes: int) -> None:
		pass

	def get_profile_summary(self) -> str:
		pass


@dataclass
class Pet:
	"""Stores pet details used by the scheduler."""

	pet_name: str
	species: str
	age: int
	energy_level: str
	special_needs: str

	def update_pet_info(self, info: dict[str, Any]) -> None:
		pass

	def get_care_needs(self) -> str:
		pass

	def get_pet_summary(self) -> str:
		pass


@dataclass
class Task:
	"""Represents a single care task that can be scheduled."""

	task_name: str
	category: str
	duration_minutes: int
	priority: int
	due_window: str
	frequency: str
	notes: str

	def edit_task(self, details: dict[str, Any]) -> None:
		pass

	def is_due_today(self, target_date: date) -> bool:
		pass

	def mark_completed(self) -> None:
		pass

	def estimate_urgency_score(self) -> float:
		pass


class Scheduler:
	"""Builds and explains a daily task plan."""

	def __init__(self, task_list: list[Task]) -> None:
		self.task_list = task_list

	def rank_tasks(self, tasks: list[Task]) -> list[Task]:
		pass

	def build_daily_plan(self, target_date: date) -> list[Task]:
		pass

	def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
		pass

	def explain_selection_logic(self) -> str:
		pass
