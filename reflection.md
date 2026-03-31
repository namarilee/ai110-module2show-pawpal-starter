# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design uses three classes: `CareTask`, `Pet`, and `DailyScheduler`.

**`CareTask`** represents one unit of care (a walk, feeding, medication, etc.). Its responsibility is to hold the task's data — title, duration in minutes, and priority — and to expose a `priority_rank()` method that converts the string priority into a number (high=3, medium=2, low=1) so the scheduler can sort tasks without comparing strings directly.

**`Pet`** is the central data container. It stores the pet's profile (name, species, age, health notes) and owns the list of `CareTask` objects. Its responsibility is to manage that list: adding, removing, and reporting total task time. It acts as the single source of truth that the scheduler reads from.

**`DailyScheduler`** is the core logic class. It takes a `Pet` and a time budget (in minutes) and produces a prioritized daily plan. Its `build()` method sorts tasks by priority rank, then greedily fits them into the available time, recording a start time and a one-line reason for each accepted task. Supporting methods — `format_schedule()` and `skipped_tasks()` — handle display and surfacing what was left out.

**b. Core user actions**

The three core actions a user should be able to perform in PawPal+ are:

1. **Add a pet** — The user enters basic information about their pet (name, species, age, and any relevant health notes). This anchors the rest of the app: tasks, schedules, and priorities are all tied to a specific pet profile. Without this step, nothing else is personalized.

2. **Add and manage care tasks** — The user creates tasks such as walks, feedings, medication reminders, grooming sessions, or enrichment activities. Each task has at minimum a duration and a priority level. The user can also edit or remove tasks as the pet's routine changes over time.

3. **Generate and view today's daily plan** — The user triggers the scheduler to produce a prioritized daily schedule based on the tasks they've entered and any time or preference constraints. The app displays the plan clearly and ideally explains why tasks were ordered or included the way they were.



**b. Design changes**

Three changes were made while reviewing the skeleton code:

1. **Added `start_hour` to `DailyScheduler`** — The original design had no way to produce real clock times (e.g., "9:00 AM", "9:20 AM") for each scheduled task. Without a starting point, `build()` could only produce meaningless offsets. Adding `start_hour: int = 9` as an `__init__` parameter (defaulting to 9 AM) gives the scheduler what it needs to compute and display human-readable start times.

2. **Added input validation to `CareTask.__init__`** — The original skeleton accepted any string for `priority`, which would cause `priority_rank()` to fail silently or return the wrong value if given `"High"` or a typo. A `VALID_PRIORITIES` class constant and two guard clauses (`ValueError` on bad priority or non-positive duration) catch bad data at construction time rather than during scheduling.

3. **Added ordering warnings to `format_schedule()` and `skipped_tasks()`** — Both methods depend on `self.schedule` being populated by `build()` first. If called out of order they return empty results with no indication of the problem. Brief docstring notes make this dependency explicit so it's harder to misuse.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler uses a **greedy algorithm**: it sorts all pending tasks by priority (high → medium → low), then walks the list from top to bottom and assigns each task to the next available time slot as long as it fits within the remaining time budget. Once a task is placed, the clock advances by its duration and the next task starts immediately after.

The tradeoff is **speed and simplicity vs. optimality**. A greedy approach is easy to read, runs in O(n log n) time (dominated by the sort), and always produces a valid schedule. However, it can miss better arrangements. For example, if the budget has 30 minutes left and the next task takes 35 minutes (skipped), but two lower-priority tasks of 10 and 15 minutes would fit together, the greedy algorithm still skips the lower-priority ones rather than backtracking to fill the gap.

This tradeoff is reasonable for a pet care app because the task lists are small (typically under 20 tasks per pet), the priority ordering reflects genuine urgency that the owner wants respected, and the cognitive overhead of explaining a backtracking optimizer to a pet owner is not worth the marginal gain. A greedy schedule that is slightly suboptimal but easy to predict is more trustworthy for everyday use than an optimal schedule that is hard to reason about.

---

## 3. AI Collaboration

**a. How you used AI**

During design, it helped brainstorm the object model, identifying which responsibilities belonged in `Task` vs. `Pet` vs. `Scheduler`, and arguing against adding an `Owner` class before deciding one was actually needed for multi-pet support. During implementation, it generated method stubs and then filled in logic incrementally, which made it easy to read and verify each piece before moving on. During refactoring, it flagged the manual `for i / for j` double-loop in `detect_conflicts()` as a readability issue and suggested replacing it with `itertools.combinations`.

The most helpful type of prompt was a constrained, specific question: "given this method signature and this docstring, implement the body" produced tighter, more reviewable code than open-ended "build a scheduler" prompts. Asking AI to explain a tradeoff — rather than just make a choice — also produced more useful output because it surfaced the reasoning, not just the answer.

**b. Judgment and verification**

When AI first proposed the conflict detection method, it used a `for i / for j in range(len(...))` pattern with index arithmetic. The logic was correct but hard to read at a glance. Rather than accepting it, the approach was tested manually against known overlapping and non-overlapping pairs, then the implementation was simplified to `itertools.combinations`, which expresses the same intent in one line with no index math. The key verification step was running the full test suite after the refactor to confirm the behavior was identical before and after the change.

---

## 4. Testing and Verification

**a. What you tested**

Thirteen automated tests cover four categories:

- **Core behavior** — `mark_complete()` flips `completed` to `True`; adding a task increases the pet's task count. These matter because they are the most fundamental operations; if they break, nothing else works.
- **Sorting** — priority sort returns high → medium → low; duration sort returns shortest first; the built schedule's `start_min` values are non-decreasing (chronological order). Sorting is the first step inside `build()`, so errors here would silently corrupt every schedule.
- **Recurrence** — daily tasks advance `next_due` by exactly 1 day; weekly by exactly 7; `as_needed` tasks leave `next_due` unchanged; a completed daily task returns `False` from `is_due_today()`. Date math is easy to get wrong by one day, and a recurrence bug would mean tasks appear on the wrong day indefinitely.
- **Conflict detection** — normal schedules produce no conflicts; same-pet and cross-pet overlaps are each flagged with the correct label; adjacent tasks that share only an endpoint are not flagged. The adjacent-task test specifically guards the `<` vs `<=` boundary in the overlap formula.

**b. Confidence**

★★★★☆ (4/5). The core scheduling logic, recurrence math, and conflict detection are all covered and passing. Two gaps remain: the Streamlit UI flow is not integration-tested (adding a task through the UI and generating a schedule is only verified manually), and the exact-fit boundary — a task whose duration equals the remaining budget to the minute — is not in the automated suite. Both work in manual testing but are not yet locked down with assertions.

---

## 5. Reflection

**a. What went well**

The layered design worked well. Because `Task`, `Pet`, `Owner`, and `Scheduler` each had a single clear responsibility, it was straightforward to add features like recurrence, filtering, conflict detection without rewriting existing methods. The greedy scheduler in particular stayed simple throughout: every new feature plugged into it rather than requiring changes to `build()` itself. The test suite also paid off immediately; when `_format_time()` was extracted from `build()` as a refactor, the tests caught no regressions and confirmed the change was safe in seconds.

**b. What you would improve**

The biggest redesign would be persisting state between sessions. Right now, closing the browser tab loses every pet, task, and schedule. Adding a simple JSON file or SQLite database behind `Owner` and `Pet` would make the app genuinely useful day-to-day rather than a single-session demo. A secondary improvement would be replacing the flat task list with a proper calendar model so the scheduler can reason about specific days rather than just "today."

**c. Key takeaway**

The most important thing learned was that designing the data model carefully at the start saves far more time than it costs. The decision to give `Task` a `next_due` date and `frequency` field from the beginning meant that recurrence, the due-today filter, and the conflict detector all had a clean, stable foundation to build on. When those features were added later, they required new methods but no changes to existing attributes which kept the tests green throughout.

