"""
main.py
-------
This is the web server (API). It uses FastAPI, a modern Python framework.

WHAT'S AN API?
An API lets the frontend (the webpage the user sees) talk to the backend
(this Python code) over HTTP. The frontend sends requests like
"add a teacher" or "generate the timetable", and this file handles them.

HOW TO RUN THIS FILE: see README.md in the project root.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import engine, get_db
import models
from scheduler import generate_timetable

# Create all database tables (if they don't already exist)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="College Timetable Generator")

# CORS lets our frontend (running on a different port/file) call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic schemas (define what valid JSON input looks like) ----------

class TeacherIn(BaseModel):
    name: str


class RoomIn(BaseModel):
    name: str


class SectionIn(BaseModel):
    name: str


class SubjectIn(BaseModel):
    name: str
    periods_per_week: int
    teacher_id: int
    section_id: int


# ---------------------------- Teacher endpoints ----------------------------

@app.post("/teachers")
def add_teacher(teacher: TeacherIn, db: Session = Depends(get_db)):
    obj = models.Teacher(name=teacher.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/teachers")
def list_teachers(db: Session = Depends(get_db)):
    return db.query(models.Teacher).all()


# ------------------------------ Room endpoints ------------------------------

@app.post("/rooms")
def add_room(room: RoomIn, db: Session = Depends(get_db)):
    obj = models.Room(name=room.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/rooms")
def list_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).all()


# ---------------------------- Section endpoints ----------------------------

@app.post("/sections")
def add_section(section: SectionIn, db: Session = Depends(get_db)):
    obj = models.Section(name=section.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/sections")
def list_sections(db: Session = Depends(get_db)):
    return db.query(models.Section).all()


# ---------------------------- Subject endpoints ----------------------------

@app.post("/subjects")
def add_subject(subject: SubjectIn, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).get(subject.teacher_id)
    section = db.query(models.Section).get(subject.section_id)
    if not teacher or not section:
        raise HTTPException(400, "Invalid teacher_id or section_id")

    obj = models.Subject(
        name=subject.name,
        periods_per_week=subject.periods_per_week,
        teacher_id=subject.teacher_id,
        section_id=subject.section_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/subjects")
def list_subjects(db: Session = Depends(get_db)):
    return db.query(models.Subject).all()


# -------------------------- Timetable generation ----------------------------

@app.post("/generate")
def generate(db: Session = Depends(get_db)):
    """
    Pulls all subjects + rooms from the DB, runs the backtracking scheduler,
    saves the result, and returns it.
    """
    subjects_db = db.query(models.Subject).all()
    rooms_db = db.query(models.Room).all()

    if not subjects_db:
        raise HTTPException(400, "Add at least one subject before generating.")
    if not rooms_db:
        raise HTTPException(400, "Add at least one room before generating.")

    subjects = [
        {
            "name": s.name,
            "teacher": s.teacher.name,
            "section": s.section.name,
            "periods_per_week": s.periods_per_week,
        }
        for s in subjects_db
    ]
    rooms = [r.name for r in rooms_db]

    success, result = generate_timetable(subjects, rooms)
    if not success:
        raise HTTPException(409, result)  # result is the error message string

    # Wipe old timetable and save the new one
    db.query(models.TimetableEntry).delete()
    for row in result:
        db.add(
            models.TimetableEntry(
                day=row["day"],
                period=row["period"],
                subject_name=row["subject"],
                teacher_name=row["teacher"],
                room_name=row["room"],
                section_name=row["section"],
            )
        )
    db.commit()

    return {"status": "success", "entries": result}


@app.get("/timetable")
def get_timetable(db: Session = Depends(get_db)):
    return db.query(models.TimetableEntry).all()


@app.get("/")
def root():
    return {"message": "College Timetable Generator API is running. See /docs"}
