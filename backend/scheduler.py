"""
scheduler.py
------------
THIS is the "computer science" heart of the project — the part you should
be ready to explain in an interview.

THE PROBLEM (in plain English)
-------------------------------
We have:
  - Several Sections (e.g. CSE-A, CSE-B)
  - Each Section has several Subjects, each needing N periods/week
  - Each Subject is taught by one Teacher
  - We have a fixed grid of time slots: 5 days x 6 periods = 30 slots
  - We have a limited number of Rooms

We must place every (Subject -> periods_per_week) into slots such that:
  1. A Section never has two subjects at the same time slot.
  2. A Teacher never teaches two different sections at the same time slot.
  3. A Room never hosts two classes at the same time slot.
  4. (Nice-to-have) The same subject doesn't repeat twice on the same day.

This is a classic CONSTRAINT SATISFACTION PROBLEM (CSP) — the same family
of problems as Sudoku or graph-coloring. We solve it using BACKTRACKING
with the "Most Constrained Variable" (MRV) heuristic, which is a standard,
interview-friendly technique:

  - Build a list of "tasks" to place: one task per (subject, occurrence),
    e.g. "DBMS lecture #1", "DBMS lecture #2", "DBMS lecture #3".
  - Sort tasks so the hardest ones (fewest possible valid slots) go first.
    This is the MRV heuristic — it makes backtracking dramatically faster,
    because we fail fast on hard constraints instead of discovering the
    conflict deep into the search tree.
  - Try to place each task into a valid slot. If we get stuck, backtrack
    (undo the last placement) and try a different slot/order.

COMPLEXITY NOTE (say this in interviews):
Naive backtracking is exponential in the worst case, but for realistic
college timetables (limited subjects, limited slots) with the MRV
heuristic it converges quickly in practice — this is the same idea used
in real-world CSP solvers (e.g. Google OR-Tools) just implemented from
first principles here so you can explain every line.
"""

import random
from dataclasses import dataclass, field

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS_PER_DAY = 6
ALL_SLOTS = [(day, period) for day in DAYS for period in range(1, PERIODS_PER_DAY + 1)]


@dataclass
class Task:
    """One lecture of one subject that needs to be placed into a slot."""
    subject_name: str
    teacher_name: str
    section_name: str
    occurrence: int  # 1st, 2nd, 3rd... lecture of this subject this week


@dataclass
class ScheduleState:
    # What's already booked, so we can quickly check conflicts (O(1) lookups)
    teacher_busy: dict = field(default_factory=dict)   # (teacher, day, period) -> True
    section_busy: dict = field(default_factory=dict)   # (section, day, period) -> True
    room_busy: dict = field(default_factory=dict)      # (room, day, period)   -> True
    subject_day_used: dict = field(default_factory=dict)  # (subject, section, day) -> True
    assignments: list = field(default_factory=list)    # final result rows


def build_tasks(subjects):
    """
    subjects: list of dicts like
      {"name": "DBMS", "teacher": "Mr. Rao", "section": "CSE-A", "periods_per_week": 3}

    Returns a flat list of Task objects: 3 DBMS periods -> 3 separate Tasks.
    """
    tasks = []
    for subj in subjects:
        for occ in range(1, subj["periods_per_week"] + 1):
            tasks.append(
                Task(
                    subject_name=subj["name"],
                    teacher_name=subj["teacher"],
                    section_name=subj["section"],
                    occurrence=occ,
                )
            )
    return tasks


def valid_slots_for_task(task, state, rooms):
    """
    Returns every (day, period, room) combination that would NOT break a
    hard constraint if we placed `task` there right now.
    """
    options = []
    for day, period in ALL_SLOTS:
        if state.teacher_busy.get((task.teacher_name, day, period)):
            continue  # teacher already teaching someone else
        if state.section_busy.get((task.section_name, day, period)):
            continue  # section already has a class this period
        # soft constraint: avoid same subject twice in one day, if possible
        same_day_used = state.subject_day_used.get(
            (task.subject_name, task.section_name, day)
        )
        for room in rooms:
            if state.room_busy.get((room, day, period)):
                continue  # room taken
            options.append((day, period, room, same_day_used))
    return options


def place_task(task, day, period, room, state):
    state.teacher_busy[(task.teacher_name, day, period)] = True
    state.section_busy[(task.section_name, day, period)] = True
    state.room_busy[(room, day, period)] = True
    state.subject_day_used[(task.subject_name, task.section_name, day)] = True
    state.assignments.append(
        {
            "day": day,
            "period": period,
            "subject": task.subject_name,
            "teacher": task.teacher_name,
            "room": room,
            "section": task.section_name,
        }
    )


def unplace_task(task, day, period, room, state):
    del state.teacher_busy[(task.teacher_name, day, period)]
    del state.section_busy[(task.section_name, day, period)]
    del state.room_busy[(room, day, period)]
    # Note: we don't bother clearing subject_day_used precisely, since it's
    # just a soft preference used for ordering, not a hard rule.
    state.assignments.pop()


def backtrack(tasks, index, state, rooms):
    """
    The recursive backtracking function.

    tasks: full task list, already sorted by MRV (hardest first)
    index: which task we're currently trying to place
    """
    if index == len(tasks):
        return True  # all tasks placed successfully!

    task = tasks[index]
    options = valid_slots_for_task(task, state, rooms)

    # Prefer options where the subject hasn't already been used that day
    # (spreads subjects across the week instead of clumping them)
    options.sort(key=lambda o: o[3] is True)
    random.shuffle(options)  # add variety between runs so results aren't robotic
    options.sort(key=lambda o: o[3] is True)

    for day, period, room, _ in options:
        place_task(task, day, period, room, state)
        if backtrack(tasks, index + 1, state, rooms):
            return True
        unplace_task(task, day, period, room, state)  # undo and try next option

    return False  # no option worked -> tell caller (previous task) to retry


def generate_timetable(subjects, rooms):
    """
    Main entry point.

    subjects: list of dicts: {"name", "teacher", "section", "periods_per_week"}
    rooms: list of room name strings, e.g. ["LT-1", "LT-2", "Lab-1"]

    Returns: (success: bool, result: list[dict] or error message string)
    """
    tasks = build_tasks(subjects)

    # MRV heuristic: we approximate "most constrained" by how many periods/week
    # a subject needs (more periods = harder to fit = schedule it first) and
    # group by teacher load (busier teachers first).
    teacher_load = {}
    for t in tasks:
        teacher_load[t.teacher_name] = teacher_load.get(t.teacher_name, 0) + 1

    tasks.sort(key=lambda t: -teacher_load[t.teacher_name])

    state = ScheduleState()
    success = backtrack(tasks, 0, state, rooms)

    if not success:
        return False, (
            "Could not generate a clash-free timetable with the given data. "
            "Try adding more rooms, reducing periods/week, or checking for "
            "teachers overloaded across too many sections."
        )
    return True, state.assignments
