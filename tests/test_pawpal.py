from pawpal_system import Task, Pet


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
