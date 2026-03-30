from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo now that the backend classes are connected.
"""
)


def get_pet_by_name(owner: Owner, pet_name: str) -> Pet | None:
    """Return the first pet with the matching name, if present."""
    for pet in owner.pets:
        if pet.pet_name == pet_name:
            return pet
    return None


# Persist the Owner instance across Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_name="Jordan",
        available_minutes_per_day=90,
        preferred_task_order=["meds", "feeding", "walk", "enrichment"],
        medication_reminder_enabled=True,
    )

owner: Owner = st.session_state.owner

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner Profile")
with st.form("owner_profile_form"):
    owner_name = st.text_input("Owner name", value=owner.owner_name)
    available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=600, value=owner.available_minutes_per_day
    )
    reminders = st.checkbox("Medication reminders", value=owner.medication_reminder_enabled)
    owner_submitted = st.form_submit_button("Save owner profile")

if owner_submitted:
    owner.owner_name = owner_name
    owner.set_daily_availability(int(available_minutes))
    owner.update_preferences({"medication_reminder_enabled": reminders})
    st.success("Owner profile updated.")

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age", min_value=0, max_value=40, value=3)
    energy_level = st.selectbox("Energy level", ["low", "medium", "high"], index=1)
    special_needs = st.text_input("Special needs", value="")
    pet_submitted = st.form_submit_button("Add pet")

if pet_submitted:
    try:
        owner.add_pet(
            Pet(
                pet_name=pet_name.strip(),
                species=species,
                age=int(age),
                energy_level=energy_level,
                special_needs=special_needs,
            )
        )
        st.success(f"Added pet: {pet_name}")
    except ValueError as exc:
        st.error(str(exc))

st.markdown("### Tasks")
st.caption("Add tasks for a selected pet. These tasks are stored in your Owner/Pet objects.")

if owner.pets:
    pet_names = [pet.pet_name for pet in owner.pets]
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox("Pet", pet_names)
        description = st.text_input("Task description", value="Morning walk")
        due_date = st.date_input("Due date", value=date.today())
        due_time = st.time_input("Due time", value=time(hour=8, minute=0))
        frequency = st.selectbox("Frequency", ["daily", "weekly", "one-time"], index=0)
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.slider("Priority", min_value=1, max_value=3, value=2)
        category = st.selectbox("Category", ["walk", "feeding", "meds", "enrichment", "grooming", "general"])
        notes = st.text_input("Notes", value="")
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        pet = get_pet_by_name(owner, selected_pet_name)
        if pet is None:
            st.error("Selected pet was not found.")
        else:
            pet.add_task(
                Task(
                    description=description,
                    due_at=datetime.combine(due_date, due_time),
                    frequency=frequency,
                    priority=int(priority),
                    duration_minutes=int(duration),
                    category=category,
                    notes=notes,
                )
            )
            st.success(f"Added task to {selected_pet_name}: {description}")
else:
    st.info("Add at least one pet before creating tasks.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": task.pet_name,
                "description": task.description,
                "due": task.due_at.strftime("%Y-%m-%d %H:%M"),
                "priority": task.priority,
                "duration_minutes": task.duration_minutes,
                "completed": task.completed,
            }
            for task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This now uses Scheduler to generate a real plan for today.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner)
    plan = scheduler.build_daily_plan(date.today())

    if plan:
        st.success("Today's Schedule")
        st.table(
            [
                {
                    "pet": task.pet_name,
                    "task": task.description,
                    "due": task.due_at.strftime("%I:%M %p"),
                    "priority": task.priority,
                    "minutes": task.duration_minutes,
                }
                for task in plan
            ]
        )
        st.caption(scheduler.explain_selection_logic())
    else:
        st.warning("No tasks were eligible for today's schedule.")
