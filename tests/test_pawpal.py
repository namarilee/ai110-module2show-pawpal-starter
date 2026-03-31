import datetime
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    """Calling mark_complete() should set task.completed to True."""
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False  # starts incomplete
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0  # starts empty
    pet.add_task(Task("Breakfast feeding", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1


# ── Sorting correctness ───────────────────────────────────────────────────────

def test_sort_by_priority_returns_high_first():
    """sort_tasks(by='priority') should put high-priority tasks before lower ones."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Low task",    duration_minutes=10, priority="low"))
    pet.add_task(Task("High task",   duration_minutes=10, priority="high"))
    pet.add_task(Task("Medium task", duration_minutes=10, priority="medium"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=120)
    sorted_pairs = scheduler.sort_tasks(owner.all_tasks(), by="priority")
    priorities = [task.priority for _, task in sorted_pairs]
    assert priorities == ["high", "medium", "low"]


def test_sort_by_duration_returns_shortest_first():
    """sort_tasks(by='duration') should order tasks from shortest to longest."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Long task",   duration_minutes=30, priority="medium"))
    pet.add_task(Task("Short task",  duration_minutes=5,  priority="medium"))
    pet.add_task(Task("Medium task", duration_minutes=15, priority="medium"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=120)
    sorted_pairs = scheduler.sort_tasks(owner.all_tasks(), by="duration")
    durations = [task.duration_minutes for _, task in sorted_pairs]
    assert durations == [5, 15, 30]


def test_build_schedule_is_chronological():
    """Tasks in the built schedule should have non-decreasing start_min values."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk",    duration_minutes=20, priority="high"))
    pet.add_task(Task("Feed",    duration_minutes=10, priority="high"))
    pet.add_task(Task("Groom",   duration_minutes=15, priority="medium"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=120, start_hour=8)
    scheduler.build()

    start_mins = [entry["start_min"] for entry in scheduler.schedule]
    assert start_mins == sorted(start_mins)


# ── Recurrence logic ──────────────────────────────────────────────────────────

def test_daily_task_next_due_advances_by_one_day():
    """Completing a daily task should set next_due to tomorrow."""
    task = Task("Morning walk", duration_minutes=30, priority="high", frequency="daily")
    task.mark_complete()
    assert task.next_due == datetime.date.today() + datetime.timedelta(days=1)


def test_weekly_task_next_due_advances_by_seven_days():
    """Completing a weekly task should set next_due to 7 days from today."""
    task = Task("Brush coat", duration_minutes=15, priority="low", frequency="weekly")
    task.mark_complete()
    assert task.next_due == datetime.date.today() + datetime.timedelta(weeks=1)


def test_as_needed_task_next_due_unchanged_after_complete():
    """Completing an as_needed task should not change next_due."""
    task = Task("Vet checkup", duration_minutes=60, priority="medium", frequency="as_needed")
    original_due = task.next_due
    task.mark_complete()
    assert task.next_due == original_due


def test_completed_daily_task_not_due_today():
    """After marking a daily task complete, is_due_today() should return False."""
    task = Task("Morning walk", duration_minutes=30, priority="high", frequency="daily")
    task.mark_complete()
    assert task.is_due_today() is False


# ── Conflict detection ────────────────────────────────────────────────────────

def test_no_conflicts_in_normal_schedule():
    """A normally built schedule should produce no conflicts."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task("Feed", duration_minutes=10, priority="high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=120, start_hour=8)
    scheduler.build()
    assert scheduler.detect_conflicts() == []


def test_same_pet_overlap_flagged_as_conflict():
    """Two overlapping tasks for the same pet should produce a same-pet conflict warning."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task("Feed", duration_minutes=10, priority="high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=120, start_hour=8)
    # Inject two entries with overlapping windows for the same pet
    scheduler.schedule = [
        {"pet": pet, "task": pet.tasks[0], "start_time": "8:00 AM",
         "reason": "", "start_min": 480, "end_min": 510},
        {"pet": pet, "task": pet.tasks[1], "start_time": "8:00 AM",
         "reason": "", "start_min": 480, "end_min": 490},
    ]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "SAME-PET" in conflicts[0]


def test_cross_pet_overlap_flagged_as_conflict():
    """Overlapping tasks across different pets should produce a cross-pet conflict warning."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", 3)
    luna  = Pet("Luna",  "cat", 5)
    mochi.add_task(Task("Walk",       duration_minutes=30, priority="high"))
    luna.add_task(Task("Medication",  duration_minutes=10, priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner, available_minutes=120, start_hour=8)
    scheduler.schedule = [
        {"pet": mochi, "task": mochi.tasks[0], "start_time": "8:00 AM",
         "reason": "", "start_min": 480, "end_min": 510},
        {"pet": luna,  "task": luna.tasks[0],  "start_time": "8:05 AM",
         "reason": "", "start_min": 485, "end_min": 495},
    ]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "CROSS-PET" in conflicts[0]


def test_adjacent_tasks_are_not_a_conflict():
    """Tasks that share only an endpoint (A ends exactly when B starts) should not conflict."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task("Feed", duration_minutes=10, priority="high"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=120, start_hour=8)
    scheduler.schedule = [
        {"pet": pet, "task": pet.tasks[0], "start_time": "8:00 AM",
         "reason": "", "start_min": 480, "end_min": 500},
        {"pet": pet, "task": pet.tasks[1], "start_time": "8:20 AM",
         "reason": "", "start_min": 500, "end_min": 510},
    ]
    assert scheduler.detect_conflicts() == []
