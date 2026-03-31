import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

st.divider()

# ── Pet & Owner Setup ────────────────────────────────────────────────────────
st.subheader("Owner & Pet Info")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name   = st.text_input("Pet name", value="Mochi")
species    = st.selectbox("Species", ["dog", "cat", "other"])
health_notes = st.text_input("Health notes (optional)", value="")

if st.button("Save pet profile"):
    owner = Owner(owner_name)
    pet = Pet(name=pet_name, species=species, age=0, health_notes=health_notes)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.pop("scheduler", None)  # reset any old schedule
    st.success(f"Profile saved — Owner: **{owner_name}** | Pet: **{pet_name}** ({species})")

st.divider()

# ── Task Management ──────────────────────────────────────────────────────────
st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_desc = st.text_input("Description", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
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
        st.success(f"Task added: **{task_desc}** ({duration} min, {priority})")

# ── Task list with sorting + filtering ───────────────────────────────────────
if "pet" in st.session_state and st.session_state.pet.tasks:
    st.divider()
    st.subheader("Current Tasks")

    # Controls
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sort_by = st.selectbox("Sort by", ["priority", "duration", "frequency", "status"])
    with fc2:
        filter_status = st.selectbox("Filter by status", ["all", "pending", "completed"])
    with fc3:
        filter_priority = st.selectbox("Filter by priority", ["all", "high", "medium", "low"])

    # Build a temporary scheduler just for filtering/sorting the task list
    temp_scheduler = Scheduler(st.session_state.owner, available_minutes=999)

    status_arg   = None if filter_status == "all" else filter_status
    priority_arg = None if filter_priority == "all" else filter_priority
    filtered = temp_scheduler.filter_tasks(
        pet_name=st.session_state.pet.name,
        status=status_arg,
        priority=priority_arg,
    )
    sorted_pairs = temp_scheduler.sort_tasks(filtered, by=sort_by)

    if sorted_pairs:
        PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
        rows = [
            {
                "Status":       "✓ done" if t.completed else "○ pending",
                "Description":  t.description,
                "Duration (min)": t.duration_minutes,
                "Priority":     PRIORITY_BADGE[t.priority],
                "Frequency":    t.frequency,
                "Next due":     str(t.next_due),
            }
            for _, t in sorted_pairs
        ]
        st.table(rows)

        total_min = sum(t.duration_minutes for _, t in sorted_pairs)
        st.caption(f"{len(rows)} task(s) shown — {total_min} total minutes")
    else:
        st.info("No tasks match the current filters.")
else:
    st.info("No tasks yet. Save a pet profile and add tasks above.")

st.divider()

# ── Schedule Generation ──────────────────────────────────────────────────────
st.subheader("Build Today's Schedule")

sc1, sc2 = st.columns(2)
with sc1:
    available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=120)
with sc2:
    start_hour = st.slider("Start hour", min_value=6, max_value=12, value=9,
                           format="%d:00")

if st.button("Generate schedule"):
    if "owner" not in st.session_state:
        st.warning("Save a pet profile first.")
    elif not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        total = st.session_state.pet.total_task_minutes()
        if total > available_minutes:
            st.warning(
                f"Total task time ({total} min) exceeds your budget ({int(available_minutes)} min). "
                "Some tasks will be skipped."
            )
        scheduler = Scheduler(
            owner=st.session_state.owner,
            available_minutes=int(available_minutes),
            start_hour=start_hour,
        )
        scheduler.build()
        st.session_state.scheduler = scheduler

if "scheduler" in st.session_state:
    sched = st.session_state.scheduler

    # ── Scheduled tasks ──────────────────────────────────────────────────────
    if sched.schedule:
        st.success(f"{len(sched.schedule)} task(s) scheduled within your {sched.available_minutes}-minute budget.")
        schedule_rows = [
            {
                "Time":           e["start_time"],
                "Pet":            e["pet"].name,
                "Task":           e["task"].description,
                "Duration (min)": e["task"].duration_minutes,
                "Priority":       e["task"].priority,
                "Reason":         e["reason"],
            }
            for e in sched.schedule
        ]
        st.table(schedule_rows)
    else:
        st.warning("No tasks could be scheduled. Check your time budget.")

    # ── Skipped tasks ─────────────────────────────────────────────────────────
    skipped = sched.skipped_tasks()
    if skipped:
        st.warning(f"{len(skipped)} task(s) didn't fit in the time budget:")
        for pet, task in skipped:
            st.markdown(f"- **[{pet.name}]** {task.description} ({task.duration_minutes} min, {task.priority})")

    # ── Conflict detection ────────────────────────────────────────────────────
    conflicts = sched.detect_conflicts()
    if conflicts:
        st.error(f"{len(conflicts)} scheduling conflict(s) detected:")
        for w in conflicts:
            st.markdown(f"- {w}")
    else:
        st.success("No scheduling conflicts detected.")
