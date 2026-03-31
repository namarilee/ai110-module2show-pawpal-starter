from pawpal_system import Task, Pet, Owner, Scheduler

# ── Setup ────────────────────────────────────────────────────────────────────
owner = Owner("Jordan")

mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

mochi.add_task(Task("Morning walk",      duration_minutes=30, priority="high",   frequency="daily"))
mochi.add_task(Task("Breakfast feeding", duration_minutes=10, priority="high",   frequency="daily"))
luna.add_task(Task("Thyroid medication", duration_minutes=5,  priority="high",   frequency="daily"))
luna.add_task(Task("Wet food feeding",   duration_minutes=10, priority="high",   frequency="daily"))

owner.add_pet(mochi)
owner.add_pet(luna)


def section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ── Scenario 1: no conflicts (normal build) ──────────────────────────────────
section("SCENARIO 1 — Normal build (no conflicts expected)")
scheduler = Scheduler(owner, available_minutes=120, start_hour=8)
scheduler.build()
for entry in scheduler.schedule:
    t = entry["task"]
    print(f"  {entry['start_time']:>8}  [{entry['pet'].name}] {t.description:<22} "
          f"{t.duration_minutes} min  [{entry['start_min']}–{entry['end_min']}]")

conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(f"\n  {w}")
else:
    print("\n  No conflicts detected.")

# ── Scenario 2: manually inject overlapping entries to trigger warnings ───────
section("SCENARIO 2 — Injected overlaps (same-pet + cross-pet conflicts)")

# Build a fresh scheduler and manually insert overlapping windows
s2 = Scheduler(owner, available_minutes=120, start_hour=8)

# Same-pet conflict: Mochi has two tasks both starting at 8:00 (480–510 and 480–490)
s2.schedule = [
    {
        "pet": mochi, "task": mochi.tasks[0],   # Morning walk 30 min
        "start_time": "8:00 AM", "reason": "injected",
        "start_min": 480, "end_min": 510,
    },
    {
        "pet": mochi, "task": mochi.tasks[1],   # Breakfast feeding 10 min — overlaps walk
        "start_time": "8:00 AM", "reason": "injected",
        "start_min": 480, "end_min": 490,
    },
    {
        "pet": luna, "task": luna.tasks[0],     # Thyroid medication 5 min — overlaps walk
        "start_time": "8:05 AM", "reason": "injected",
        "start_min": 485, "end_min": 490,
    },
    {
        "pet": luna, "task": luna.tasks[1],     # Wet food feeding — no overlap
        "start_time": "8:35 AM", "reason": "injected",
        "start_min": 515, "end_min": 525,
    },
]

for entry in s2.schedule:
    t = entry["task"]
    print(f"  {entry['start_time']:>8}  [{entry['pet'].name}] {t.description:<22} "
          f"{t.task.duration_minutes if hasattr(entry['task'], 'task') else t.duration_minutes} min  "
          f"[{entry['start_min']}–{entry['end_min']}]")

print()
conflicts2 = s2.detect_conflicts()
if conflicts2:
    for w in conflicts2:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

print(f"\n{'─' * 60}\n")
