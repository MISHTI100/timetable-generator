# College Timetable Generator

A full-stack web app that automatically generates a clash-free college
timetable using a **Constraint Satisfaction Problem (CSP) solved with
backtracking + the MRV heuristic** — a real algorithm, not just a form
that saves to a database.

This doc assumes **zero prior setup knowledge**. Follow it top to bottom.

---

## 1. What this project actually does

You tell it:
- your **teachers** (e.g. "Mr. Rao")
- your **rooms** (e.g. "LT-1")
- your **sections/classes** (e.g. "CSE-A")
- your **subjects**, each with a teacher, a section, and how many periods
  per week it needs (e.g. "DBMS, taught by Mr. Rao, to CSE-A, 4 periods/week")

Click **Generate Timetable**, and the backend automatically places every
subject into a Monday–Friday, 6-period-a-day grid such that:

- No teacher is double-booked at the same time.
- No section has two classes at the same time.
- No room hosts two classes at the same time.
- (Bonus) The same subject isn't repeated twice in one day if avoidable.

This is the same category of problem as Sudoku-solving or exam-timetabling —
genuinely useful to explain in an interview, because it shows you understand
**CSP / backtracking / heuristics** (core CS fundamentals), not just CRUD.

---

## 2. Tech stack (and why)

| Layer      | Tech                     | Why |
|------------|--------------------------|-----|
| Algorithm  | Pure Python (backtracking + MRV heuristic) | Shows DSA fundamentals — no black-box library doing the thinking for you |
| Backend/API| FastAPI                  | Modern, fast, auto-generates API docs, used heavily in real companies |
| Database   | SQLite + SQLAlemy ORM    | Zero setup, file-based, still "real" SQL underneath |
| Frontend   | Plain HTML/CSS/JS        | No build tools needed — anyone can open and run it immediately |

You can later swap SQLite for PostgreSQL and the frontend for React without
touching the algorithm — that separation of concerns is itself worth
mentioning in interviews.

---

## 3. Folder structure

```
timetable-generator/
├── backend/
│   ├── main.py          <- the API server (FastAPI routes)
│   ├── scheduler.py      <- THE ALGORITHM (backtracking CSP solver)
│   ├── models.py          <- database table definitions
│   ├── database.py         <- database connection setup
│   └── requirements.txt
├── frontend/
│   └── index.html          <- the entire UI (open this in a browser)
└── README.md                <- you are here
```

---

## 4. Setup — step by step

### Step 1: Install Python
You need **Python 3.9+**. Check with:
```bash
python3 --version
```
If you don't have it, download from https://www.python.org/downloads/

### Step 2: Open a terminal in the `backend` folder
```bash
cd timetable-generator/backend
```

### Step 3: (Recommended) create a virtual environment
This keeps this project's packages separate from everything else on your
machine.
```bash
python3 -m venv venv

# Activate it:
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 4: Install the required packages
```bash
pip install -r requirements.txt
```

### Step 5: Start the backend server
```bash
uvicorn main:app --reload
```
You should see something like:
```
Uvicorn running on http://127.0.0.1:8000
```
Leave this terminal running. Visit **http://localhost:8000/docs** in your
browser — FastAPI auto-generates an interactive API testing page for you.
This alone is a great thing to show in an interview/demo.

### Step 6: Open the frontend
Just double-click `frontend/index.html`, or open it via
`File -> Open` in your browser. No server needed for the frontend — it's
a static file that talks to your backend over the API.

> If your browser blocks the request (CORS/security warnings when opening
> a local file), instead run a tiny local server for the frontend too:
> ```bash
> cd frontend
> python3 -m http.server 5500
> ```
> then visit **http://localhost:5500**.

### Step 7: Use it
1. Add a few teachers.
2. Add a few rooms.
3. Add one or more sections (e.g. CSE-A, CSE-B).
4. Add subjects — pick the teacher, section, and periods/week for each.
5. Click **Generate Timetable**.
6. Switch between section tabs to see each class's weekly grid.

---

## 5. How the algorithm works (read this before your interview)

Open `backend/scheduler.py` — every function is commented, but here's the
mental model:

1. **Break the problem into "tasks."** If DBMS needs 4 periods/week, that's
   4 separate tasks to place: "DBMS lecture 1", "DBMS lecture 2", etc.

2. **Order tasks by difficulty (MRV heuristic).** We schedule the busiest
   teachers' subjects first. Why? Because if a heavily-loaded teacher can't
   be fit in, you want to discover that failure early — not after wasting
   time placing 50 easy subjects first. This is the "Minimum Remaining
   Values" heuristic from classic CSP theory (same idea Sudoku solvers use).

3. **Backtracking search.** For each task, try every valid (day, period,
   room) combination that doesn't clash with anything already placed. Place
   it, then recursively try to place the *next* task. If a later task turns
   out to be impossible no matter what, undo (**backtrack**) the previous
   placement and try a different slot.

4. **Hard constraints vs soft constraints.**
   - Hard (never violated): teacher/section/room double-booking.
   - Soft (preferred, not mandatory): don't repeat a subject twice in one
     day. The algorithm tries to honor this by sorting options, but will
     violate it rather than fail completely.

5. **Why this matters for a 20 LPA interview:** this is a textbook
   **CSP / backtracking** problem — the same family as N-Queens, Sudoku,
   and graph coloring. Being able to explain *why* you added the MRV
   heuristic (to prune the search space and avoid exponential blow-up) is
   exactly the kind of algorithmic reasoning strong interviewers probe for.

---

## 6. Ideas to extend this (great for a standout resume bullet)

Pick 1–2 of these to implement and mention "I additionally built X":

- **Teacher unavailability**: let teachers mark slots they can't teach
  (e.g. Friday afternoons) — add this as another hard constraint.
- **Room types**: labs vs lecture halls, so a "DBMS Lab" only gets scheduled
  into rooms marked as labs.
- **Elective clashes**: prevent two electives students might take together
  from overlapping.
- **Export to PDF/Excel** using a library like `openpyxl` or `reportlab`.
- **Authentication** so only admins can generate/edit timetables.
- **Deploy it**: host the backend on Render/Railway and the frontend on
  Vercel/Netlify, so you have a live demo link to put on your resume —
  this matters a lot more than people think.
- **Swap backtracking for a Genetic Algorithm** as an alternative solver and
  compare performance — great "I explored trade-offs" talking point.

---

## 7. How to talk about this project in an interview (short script)

> "I built a college timetable generator that solves scheduling as a
> constraint satisfaction problem. I modeled every lecture as a task with
> hard constraints — no teacher, section, or room can be double-booked —
> and solved it with backtracking search, using the MRV heuristic to order
> the hardest-to-place subjects first, which cut down the search space
> significantly. The backend is a FastAPI REST API backed by SQLite through
> SQLAlchemy, and the frontend is a lightweight JS app that renders the
> generated timetable per section. I chose to write the algorithm from
> scratch rather than use a solver library like OR-Tools, specifically so I
> could reason about and explain every constraint and trade-off."

That's a strong, specific, technically credible answer — far better than
"I made a scheduling app with a database."

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `Could not generate a clash-free timetable...` | You've over-constrained it — e.g. one teacher assigned too many periods across sections for the number of slots available. Add more rooms, reduce periods/week, or split subjects across more teachers. |
| Frontend shows no data / network errors | Make sure the backend terminal is still running and showing `Uvicorn running on http://127.0.0.1:8000`. |
| `ModuleNotFoundError` | You forgot to `pip install -r requirements.txt`, or your virtual environment isn't activated. |
| Port 8000 already in use | Run `uvicorn main:app --reload --port 8001` and update the `API` constant at the top of `frontend/index.html`'s `<script>` to match. |
