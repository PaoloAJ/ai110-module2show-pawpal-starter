# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- my initial uml design had four classes: task, pet, owner, and scheduler.
- task holds the details of a single activity — what it is, when it happens, how often, and whether it's done.
- pet stores the pet's info (name, species, age) and keeps a list of its tasks.
- owner manages multiple pets and can pull all tasks from all of them into one list.
- scheduler is the brain — it connects to the owner and handles sorting, filtering, conflict detection, and recurring task logic.
- i used python dataclasses for task, pet, and owner to keep the code clean and avoid writing boilerplate init methods.

**b. Design changes**

- yes, my design changed during implementation. originally i had the scheduler directly holding a list of tasks, but i changed it so the scheduler talks to the owner to get tasks from all pets. this makes more sense because the owner is the source of truth for which pets exist and what tasks they have. it also means adding a new pet automatically makes its tasks visible to the scheduler without any extra wiring.
- i also added a `pet_name` field to the task class so that when all tasks are collected together, you can still tell which pet each one belongs to. this wasn't in my original uml but became necessary when building filtering.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- my scheduler considers time (when a task is scheduled), priority (high/medium/low), and frequency (once/daily/weekly).
- time is the main sorting key because a pet owner needs to see their day in chronological order. priority is used as a secondary view so they can focus on what matters most.
- i decided time mattered most because a daily routine is driven by the clock — you need to know what's next, not just what's important.

**b. Tradeoffs**

- one tradeoff is that conflict detection only checks for exact time matches, not overlapping durations. for example, if a 30-minute walk starts at 08:00 and a feeding is at 08:15, the system won't flag that as a conflict. this is reasonable for a simple pet care app because most tasks are short and owners usually schedule things at round times. checking for duration overlap would add complexity that isn't needed for the typical use case.

---

## 3. AI Collaboration

**a. How you used AI**

- i used ai tools throughout the project for design brainstorming, scaffolding class skeletons, generating test cases, and debugging small issues.
- the most helpful prompts were specific ones like "create a mermaid class diagram for a pet care app with these four classes" and "write pytest tests that cover sorting, recurrence, and conflict detection."
- asking ai to review my skeleton and suggest missing relationships was also useful — it caught that i needed the pet_name field on tasks early on.

**b. Judgment and verification**

- one time ai suggested adding a full priority queue with heapq for task sorting. i rejected that because python's built-in sorted() with a lambda key is simpler and perfectly fine for the scale of this app. using heapq would have added complexity without any real benefit since we're sorting at most a few dozen tasks.
- i verified ai suggestions by running them through main.py first to see the output, then writing pytest tests to lock in the expected behavior.

---

## 4. Testing and Verification

**a. What you tested**

- i tested task completion (mark_complete changes status), task addition (adding to a pet increases count), sorting by time and priority, filtering by pet and status, conflict detection for same-time tasks, recurring task creation for daily tasks, and edge cases like a pet with no tasks.
- these tests are important because they cover the core behaviors that the scheduler relies on. if sorting breaks, the whole daily schedule is wrong. if recurrence breaks, daily tasks disappear after one completion.

**b. Confidence**

- i'm fairly confident the scheduler works correctly — 4 out of 5 stars.
- if i had more time, i'd test overlapping time ranges (not just exact matches), tasks with invalid time formats, and the streamlit session state behavior to make sure data persists correctly across reruns.

---

## 5. Reflection

**a. What went well**

- i'm most satisfied with how clean the class structure turned out. the separation between owner, pet, task, and scheduler makes it easy to understand and extend. the cli-first workflow (building main.py before the ui) was really helpful — it let me verify logic without dealing with streamlit's rerun behavior.

**b. What you would improve**

- if i had another iteration, i'd add duration-aware conflict detection and a way to persist data (like saving to a json file) so tasks don't disappear when the app restarts. i'd also add more advanced scheduling like auto-suggesting optimal times based on the owner's free slots.

**c. Key takeaway**

- the most important thing i learned is that ai is great at scaffolding and generating boilerplate, but the human needs to be the architect. i had to make decisions about what to keep simple vs. what to make smart, and ai couldn't make those tradeoff calls for me. being the lead architect means knowing when to say "that's good enough" and when to push for something better.
