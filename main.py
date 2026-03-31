from pawpal_system import Task, Pet, Owner, Scheduler

# --- Set up owner ---
owner = Owner("Jordan")

# --- Create pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna = Pet(name="Luna", species="cat", age=5, health_notes="Needs thyroid medication with food")

# --- Add tasks to Mochi ---
mochi.add_task(Task("Morning walk", duration_minutes=30, priority="high", frequency="daily"))
mochi.add_task(Task("Breakfast feeding", duration_minutes=10, priority="high", frequency="daily"))
mochi.add_task(Task("Fetch / play session", duration_minutes=20, priority="medium", frequency="daily"))

# --- Add tasks to Luna ---
luna.add_task(Task("Thyroid medication", duration_minutes=5, priority="high", frequency="daily"))
luna.add_task(Task("Wet food feeding", duration_minutes=10, priority="high", frequency="daily"))
luna.add_task(Task("Brush coat", duration_minutes=15, priority="low", frequency="weekly"))

# --- Register pets with owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Build today's schedule (2-hour budget, starting at 8 AM) ---
scheduler = Scheduler(owner, available_minutes=120, start_hour=8)
scheduler.build()

# --- Print results ---
print("=" * 50)
print("       PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 50)
print(f"Owner : {owner.name}")
print(f"Pets  : {', '.join(p.name for p in owner.pets)}")
print(f"Budget: {scheduler.available_minutes} minutes starting at {scheduler.start_hour}:00 AM")
print()

for entry in scheduler.schedule:
    task = entry["task"]
    print(f"  {entry['start_time']:>8}  [{entry['pet'].name}]  {task.description}")
    print(f"            {task.duration_minutes} min  |  priority: {task.priority}  |  {task.frequency}")
    print(f"            {entry['reason']}")
    print()

skipped = scheduler.skipped_tasks()
if skipped:
    print("-" * 50)
    print("  Could not fit into today's schedule:")
    for pet, task in skipped:
        print(f"    - [{pet.name}] {task.description} ({task.duration_minutes} min, {task.priority})")
    print()

print("=" * 50)
