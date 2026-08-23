"""
database.py
-----------
Sets up a connection to a local SQLite database file (timetable.db).
SQLite = a database that lives in a single file on disk. No server needed.
Perfect for a project / demo / resume project.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./timetable.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI will call this for every request that needs the database.
    It opens a session, hands it to the request, then closes it afterwards
    (the 'finally' block guarantees cleanup even if something errors out).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
