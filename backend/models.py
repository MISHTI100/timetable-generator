"""
models.py
---------
This file defines the "shape" of our data using SQLAlchemy (a Python library
that lets us talk to a database using Python classes instead of raw SQL).

Think of each class below as a spreadsheet table:
- Teacher   -> list of teachers
- Room      -> list of rooms (classrooms/labs)
- Section   -> list of class groups, e.g. "CSE-A", "CSE-B"
- Subject   -> list of subjects, linked to a teacher and a section,
               with how many periods/week it needs
- TimetableEntry -> the FINAL generated timetable (day, period, subject, room)
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    subjects = relationship("Subject", back_populates="teacher")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Section(Base):
    """A section is a batch/class, e.g. 'CSE-A' (30-60 students)."""
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    subjects = relationship("Subject", back_populates="section")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    periods_per_week = Column(Integer, nullable=False, default=3)

    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    section_id = Column(Integer, ForeignKey("sections.id"))

    teacher = relationship("Teacher", back_populates="subjects")
    section = relationship("Section", back_populates="subjects")


class TimetableEntry(Base):
    """
    One row = one scheduled class.
    e.g. Monday, Period 2, Subject 'DBMS', Teacher 'Mr. Rao', Room 'LT-1', Section 'CSE-A'
    """
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(String, nullable=False)          # "Monday"
    period = Column(Integer, nullable=False)       # 1..6
    subject_name = Column(String, nullable=False)
    teacher_name = Column(String, nullable=False)
    room_name = Column(String, nullable=False)
    section_name = Column(String, nullable=False)
