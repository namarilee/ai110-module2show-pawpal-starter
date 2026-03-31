# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Priority-based greedy scheduling** — `Scheduler.build()` sorts all pending tasks by priority (high → medium → low), breaks ties by shortest duration, then greedily assigns tasks to time slots until the daily time budget is exhausted. Produces a guaranteed-valid schedule in O(n log n) time.

- **Daily and weekly recurrence** — Each task carries a `frequency` (`daily`, `weekly`, `as_needed`) and a `next_due` date. `mark_complete()` automatically advances `next_due` by 1 day for daily tasks and 7 days for weekly tasks. `is_due_today()` lets the scheduler include only tasks that are currently due, so a weekly grooming session only appears on the right day.

- **Sorting by priority, duration, frequency, or status** — `Scheduler.sort_tasks()` reorders any task list by four keys: priority rank (high first), duration (shortest first), frequency (daily before weekly before as-needed), or completion status (pending before done).

- **Filtering by pet, status, frequency, and priority** — `Scheduler.filter_tasks()` accepts any combination of `pet_name`, `status`, `frequency`, and `priority` to return a focused subset of tasks across all pets. Filters can be combined freely.

- **Conflict detection with interval overlap** — `Scheduler.detect_conflicts()` checks every pair of scheduled entries using the standard interval overlap test (`A.start < B.end and B.start < A.end`). Returns plain-English warning strings for same-pet conflicts (two tasks for one pet at the same time) and cross-pet conflicts (tasks across different pets that overlap). Never crashes — always returns a list.

- **Skipped task reporting** — Tasks that don't fit within the time budget are collected by `skipped_tasks()` and surfaced separately in the UI so the owner knows what was left out and why.

- **Pre-schedule overflow warning** — Before building, the app compares total task time against the available budget and warns the owner if tasks will need to be dropped, so there are no surprises after generating the schedule.

- **Multi-pet support** — The `Owner` class manages any number of pets. The scheduler operates across all of them, interleaving tasks from different pets in priority order within a single daily plan.

---

## Smarter Scheduling

Beyond the basic daily plan, PawPal+ includes several logic improvements that make the scheduler more useful for real pet care routines.

**Recurring tasks**
Tasks carry a `frequency` (`daily`, `weekly`, or `as_needed`) and a `next_due` date. Calling `mark_complete()` on a daily task automatically advances `next_due` to tomorrow; a weekly task advances it by 7 days. `as_needed` tasks stay completed until the owner re-adds them. `is_due_today()` lets the scheduler skip tasks that aren't due yet, so a weekly grooming session only appears on the right day.

**Filtering and sorting**
`Scheduler.filter_tasks()` accepts any combination of `pet_name`, `status` (`pending`/`completed`), `frequency`, and `priority` to narrow down the task list. `Scheduler.sort_tasks()` reorders any task list by `priority`, `duration`, `frequency`, or `status`. Both methods work on the live task list independently of the built schedule.

**Conflict detection**
`Scheduler.detect_conflicts()` checks every pair of scheduled entries for overlapping time windows using the standard interval overlap test (`A.start < B.end and B.start < A.end`). It returns plain-English warning strings — one per conflict — rather than crashing. It distinguishes between same-pet conflicts (one owner can't do two things for the same pet at once) and cross-pet conflicts (can't walk one pet while medicating another).

**Greedy scheduling with priority**
The core `build()` algorithm sorts tasks by priority rank (high → medium → low), breaks ties by shortest duration, then greedily fits tasks into the available time budget. Tasks that don't fit are surfaced by `skipped_tasks()`. This approach is O(n log n), easy to predict, and respects the urgency the owner has assigned — see `reflection.md` Section 2b for the full tradeoff discussion.

---

## Testing PawPal+

### Running the tests

```bash
source .venv/bin/activate
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Category | Tests | What is verified |
|---|---|---|
| **Core behavior** | 2 | `mark_complete()` flips `completed` to `True`; adding a task increases the pet's task count |
| **Sorting** | 3 | Priority sort returns high → medium → low; duration sort returns shortest first; built schedule entries are in chronological order |
| **Recurrence** | 4 | Daily tasks advance `next_due` by 1 day; weekly tasks advance by 7 days; `as_needed` tasks leave `next_due` unchanged; a completed daily task is no longer due today |
| **Conflict detection** | 4 | A normal schedule has no conflicts; same-pet overlaps are flagged; cross-pet overlaps are flagged; adjacent tasks (touching but not overlapping) are not flagged |

**Total: 13 tests, all passing.**

### Confidence level

★★★★☆ (4/5)

The core scheduling logic, recurrence math, and conflict detection are all covered and passing. The main gaps are integration tests (the full UI flow through Streamlit is untested) and edge cases around the time budget boundary (e.g., a task that exactly equals the remaining minutes). Those scenarios work in manual testing but are not yet in the automated suite.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 📸 Demo
<a href="/course_images/ai110/app_screenshot.png" target="_blank"><img src='/course_images/ai110/app_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
