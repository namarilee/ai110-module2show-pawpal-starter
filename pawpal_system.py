class CareTask:
    """Represents one unit of pet care (e.g., walk, feeding, medication)."""

    def __init__(self, title: str, duration_minutes: int, priority: str):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low", "medium", or "high"

    def priority_rank(self) -> int:
        """Return a numeric rank for sorting: high=3, medium=2, low=1."""
        pass

    def __repr__(self) -> str:
        """Return a readable string like 'Morning walk (20 min, high)'."""
        pass


class Pet:
    """Stores a pet's profile and its list of care tasks."""

    def __init__(self, name: str, species: str, age: int, health_notes: str = ""):
        self.name = name
        self.species = species  # "dog", "cat", or "other"
        self.age = age
        self.health_notes = health_notes
        self.tasks: list[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        """Append a CareTask to this pet's task list."""
        pass

    def remove_task(self, title: str) -> bool:
        """Remove the first task matching the given title. Returns True if found."""
        pass

    def total_task_minutes(self) -> int:
        """Return the sum of duration_minutes across all tasks."""
        pass


class DailyScheduler:
    """Generates a prioritized daily care plan for a pet within a time budget."""

    def __init__(self, pet: Pet, available_minutes: int):
        self.pet = pet
        self.available_minutes = available_minutes
        self.schedule: list[dict] = []  # each entry: {"task": CareTask, "start_time": str, "reason": str}

    def build(self) -> list[dict]:
        """Sort tasks by priority, greedily fit them into the time budget, return the schedule."""
        pass

    def format_schedule(self) -> str:
        """Convert self.schedule into a readable markdown string for display."""
        pass

    def skipped_tasks(self) -> list[CareTask]:
        """Return tasks from pet.tasks that did not fit into the schedule."""
        pass
