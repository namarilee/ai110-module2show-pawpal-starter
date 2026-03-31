import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

st.divider()

# ── Pet & Owner Setup ────────────────────────────────────────────────────────
st.subheader("Owner & Pet Info")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
health_notes = st.text_input("Health notes (optional)", value="")

if st.button("Save pet profile"):
    owner = Owner(owner_name)
    pet = Pet(name=pet_name, species=species, age=0, health_notes=health_notes)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Profile saved! Owner: {owner_name} | Pet: {pet_name} ({species})")

st.divider()

# ── Task Management ──────────────────────────────────────────────────────────
st.subheader("Tasks")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_desc = st.text_input("Task description", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])

if st.button("Add task"):
    if "pet" not in st.session_state:
        st.warning("Save a pet profile first before adding tasks.")
    else:
        new_task = Task(
            description=task_desc,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
        )
        st.session_state.pet.add_task(new_task)
        st.success(f"Added: {new_task}")

# Display current tasks
if "pet" in st.session_state and st.session_state.pet.tasks:
    st.markdown("**Current tasks:**")
    task_rows = [
        {
            "Description": t.description,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
            "Frequency": t.frequency,
            "Done": t.completed,
        }
        for t in st.session_state.pet.tasks
    ]
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Schedule Generation ──────────────────────────────────────────────────────
st.subheader("Build Schedule")

available_minutes = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=120)
start_hour = st.slider("Start hour (24h)", min_value=6, max_value=12, value=9)

if st.button("Generate schedule"):
    if "owner" not in st.session_state:
        st.warning("Save a pet profile first.")
    elif not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            available_minutes=int(available_minutes),
            start_hour=start_hour,
        )
        scheduler.build()
        st.session_state.scheduler = scheduler

if "scheduler" in st.session_state:
    sched = st.session_state.scheduler
    st.markdown("### Today's Schedule")
    st.markdown(sched.format_schedule())

    skipped = sched.skipped_tasks()
    if skipped:
        st.warning("These tasks didn't fit in the time budget:")
        for pet, task in skipped:
            st.markdown(f"- **[{pet.name}]** {task.description} ({task.duration_minutes} min, {task.priority})")
