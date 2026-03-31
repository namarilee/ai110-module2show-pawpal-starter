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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
