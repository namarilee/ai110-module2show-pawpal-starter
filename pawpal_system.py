import datetime
import itertools


class Task:
    """Represents a single pet care activity."""

    VALID_PRIORITIES = ("low", "medium", "high")
    VALID_FREQUENCIES = ("daily", "weekly", "as_needed")

    def __init__(
        self,
        description: str,
        duration_minutes: int,
        priority: str,
        frequency: str = "daily",
    ):
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {self.VALID_PRIORITIES}, got {priority!r}")
        if frequency not in self.VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {self.VALID_FREQUENCIES}, got {frequency!r}")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be a positive integer")

        self.description = description          # e.g. "Morning walk"
        self.duration_minutes = duration_minutes
        self.priority = priority                # "low", "medium", or "high"
        self.frequency = frequency              # "daily", "weekly", or "as_needed"
        self.completed = False                  # toggled when the task is marked done
        self.next_due: datetime.date = datetime.date.today()  # date this task is next due

    def mark_complete(self) -> None:
        """Mark this task complete and automatically schedule the next occurrence.

        - daily tasks become due again tomorrow
        - weekly tasks become due again in 7 days
        - as_needed tasks stay completed (no automatic recurrence)
        """
        self.completed = True
        if self.frequency == "daily":
            self.next_due = datetime.date.today() + datetime.timedelta(days=1)
        elif self.frequency == "weekly":
            self.next_due = datetime.date.today() + datetime.timedelta(weeks=1)
        # as_needed: no next_due update — owner re-adds when relevant

    def is_due_today(self) -> bool:
        """Return True if this task is due today or overdue (next_due <= today)."""
        return self.next_due <= datetime.date.today()

    def reset(self) -> None:
        """Reset completion status without changing next_due (used for day-rollover)."""
        self.completed = False

    def priority_rank(self) -> int:
        """Return a numeric rank for sorting: high=3, medium=2, low=1."""
        ranks = {"high": 3, "medium": 2, "low": 1}
        return ranks[self.priority]

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return (f"{self.description} ({self.duration_minutes} min, {self.priority}, "
                f"{self.frequency}, {status}, due {self.next_due})")


class Pet:
    """Stores a pet's profile and its list of tasks."""

    def __init__(self, name: str, species: str, age: int, health_notes: str = ""):
        self.name = name
        self.species = species      # "dog", "cat", or "other"
        self.age = age
        self.health_notes = health_notes
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove the first task whose description matches. Returns True if found."""
        for task in self.tasks:
            if task.description == description:
                self.tasks.remove(task)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that have not been marked complete."""
        return [t for t in self.tasks if not t.completed]

    def total_task_minutes(self) -> int:
        """Return the total duration of all tasks (complete and pending)."""
        return sum(t.duration_minutes for t in self.tasks)

    def __repr__(self) -> str:
        return f"{self.name} ({self.species}, age {self.age})"


class Owner:
    """Manages one or more pets and provides access to all their tasks."""

    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Returns True if found and removed."""
        for pet in self.pets:
            if pet.name == pet_name:
                self.pets.remove(pet)
                return True
        return False

    def get_pet(self, pet_name: str) -> Pet | None:
        """Return the Pet with the given name, or None if not found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def all_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair where the task is not yet complete."""
        return [(pet, task) for pet in self.pets for task in pet.get_pending_tasks()]

    def __repr__(self) -> str:
        return f"Owner({self.name}, {len(self.pets)} pet(s))"


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner, available_minutes: int, start_hour: int = 9):
        self.owner = owner
        self.available_minutes = available_minutes  # total time budget for the day
        self.start_hour = start_hour                # starting hour (24h clock), default 9 AM
        self.schedule: list[dict] = []              # populated by build()
        # each entry: {"pet": Pet, "task": Task, "start_time": str, "reason": str,
        #              "start_min": int, "end_min": int}

    def build(self) -> list[dict]:
        """Build a prioritized daily schedule across all pets within the time budget.

        Algorithm:
        1. Collect all pending tasks from every pet.
        2. Sort by priority rank (high first); break ties by duration (shorter first).
        3. Greedily assign tasks to time slots until the budget is exhausted.
        4. Record start time and a reason string for each accepted task.
        """
        self.schedule = []
        pending = self.owner.all_pending_tasks()

        # Sort: highest priority first, then shortest duration to maximize task count on ties
        sorted_tasks = sorted(pending, key=lambda pt: (-pt[1].priority_rank(), pt[1].duration_minutes))

        minutes_used = 0
        for pet, task in sorted_tasks:
            if minutes_used + task.duration_minutes > self.available_minutes:
                continue  # skip tasks that don't fit; keep trying smaller ones
            total_minutes = self.start_hour * 60 + minutes_used
            start_time = self._format_time(total_minutes)
            reason = f"Priority: {task.priority} — fits within remaining time ({self.available_minutes - minutes_used} min left)"
            self.schedule.append({
                "pet": pet,
                "task": task,
                "start_time": start_time,
                "reason": reason,
                "start_min": total_minutes,
                "end_min": total_minutes + task.duration_minutes,
            })
            minutes_used += task.duration_minutes

        return self.schedule

    def _format_time(self, total_minutes: int) -> str:
        """Convert an absolute minute offset into a 12-hour clock string (e.g. '9:05 AM')."""
        hour, minute = divmod(total_minutes, 60)
        period = "AM" if hour < 12 else "PM"
        display_hour = hour % 12 or 12
        return f"{display_hour}:{minute:02d} {period}"

    def detect_conflicts(self) -> list[str]:
        """Return a list of warning strings for any overlapping task windows.

        Two tasks conflict when their time windows overlap:
            A.start_min < B.end_min  and  B.start_min < A.end_min

        Covers both same-pet conflicts (one owner can't do two things at once)
        and cross-pet conflicts (e.g. walking Mochi while medicating Luna).
        Returns an empty list when no conflicts are found.
        Call build() first.
        """
        warnings = []
        for a, b in itertools.combinations(self.schedule, 2):
            if a["start_min"] < b["end_min"] and b["start_min"] < a["end_min"]:
                conflict_type = "same-pet conflict" if a["pet"].name == b["pet"].name else "cross-pet conflict"
                warnings.append(
                    f"⚠ {conflict_type.upper()}: "
                    f"[{a['pet'].name}] '{a['task'].description}' ({a['start_time']}, {a['task'].duration_minutes} min) "
                    f"overlaps with "
                    f"[{b['pet'].name}] '{b['task'].description}' ({b['start_time']}, {b['task'].duration_minutes} min)"
                )
        return warnings

    def format_schedule(self) -> str:
        """Return a markdown string of the built schedule, suitable for st.markdown().
        Call build() first."""
        if not self.schedule:
            return "_No tasks scheduled. Add tasks and call build() first._"
        lines = ["| Time | Pet | Task | Duration | Priority |",
                 "|------|-----|------|----------|----------|"]
        for entry in self.schedule:
            t = entry["task"]
            lines.append(
                f"| {entry['start_time']} | {entry['pet'].name} | {t.description} "
                f"| {t.duration_minutes} min | {t.priority} |"
            )
        return "\n".join(lines)

    def skipped_tasks(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs that were not included in the schedule.
        Call build() first."""
        scheduled_tasks = {id(entry["task"]) for entry in self.schedule}
        return [
            (pet, task)
            for pet, task in self.owner.all_pending_tasks()
            if id(task) not in scheduled_tasks
        ]

    def mark_task_complete(self, description: str, pet_name: str) -> bool:
        """Find a task by description and pet name and mark it complete.
        Returns True if found."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False
        for task in pet.tasks:
            if task.description == description:
                task.mark_complete()
                return True
        return False

    def due_today(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs that are due today and not yet completed."""
        return [
            (pet, task)
            for pet, task in self.owner.all_tasks()
            if task.is_due_today() and not task.completed
        ]

    def filter_tasks(
        self,
        pet_name: str | None = None,
        status: str | None = None,
        frequency: str | None = None,
        priority: str | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs filtered by any combination of:
        - pet_name:  exact pet name string
        - status:    "pending" or "completed"
        - frequency: "daily", "weekly", or "as_needed"
        - priority:  "low", "medium", or "high"
        """
        results = self.owner.all_tasks()
        if pet_name is not None:
            results = [(p, t) for p, t in results if p.name == pet_name]
        if status == "pending":
            results = [(p, t) for p, t in results if not t.completed]
        elif status == "completed":
            results = [(p, t) for p, t in results if t.completed]
        if frequency is not None:
            results = [(p, t) for p, t in results if t.frequency == frequency]
        if priority is not None:
            results = [(p, t) for p, t in results if t.priority == priority]
        return results

    def sort_tasks(
        self,
        tasks: list[tuple[Pet, Task]],
        by: str = "priority",
    ) -> list[tuple[Pet, Task]]:
        """Sort a (pet, task) list by one of:
        - "priority":  high → medium → low, shortest duration breaks ties
        - "duration":  shortest first
        - "frequency": daily → weekly → as_needed
        - "status":    pending first, completed last
        """
        frequency_rank = {"daily": 0, "weekly": 1, "as_needed": 2}
        if by == "priority":
            return sorted(tasks, key=lambda pt: (-pt[1].priority_rank(), pt[1].duration_minutes))
        elif by == "duration":
            return sorted(tasks, key=lambda pt: pt[1].duration_minutes)
        elif by == "frequency":
            return sorted(tasks, key=lambda pt: frequency_rank[pt[1].frequency])
        elif by == "status":
            return sorted(tasks, key=lambda pt: pt[1].completed)  # False (pending) sorts before True
        else:
            raise ValueError(f"Unknown sort key {by!r}. Choose: priority, duration, frequency, status")

    def reset_all_tasks(self) -> None:
        """Reset completion status on every task across all pets (call at day rollover)."""
        for _, task in self.owner.all_tasks():
            task.reset()

    def __repr__(self) -> str:
        return (f"Scheduler(owner={self.owner.name}, "
                f"budget={self.available_minutes} min, "
                f"scheduled={len(self.schedule)} tasks)")
