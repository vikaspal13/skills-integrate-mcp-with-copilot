import sqlite3
from contextlib import contextmanager
from typing import List, Dict

DB_PATH = "activities.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                name TEXT PRIMARY KEY,
                description TEXT,
                schedule TEXT,
                max_participants INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                activity_name TEXT,
                email TEXT,
                PRIMARY KEY (activity_name, email),
                FOREIGN KEY (activity_name) REFERENCES activities(name)
            )
        ''')
        conn.commit()

def get_all_activities() -> Dict[str, dict]:
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM activities")
        activities = {}
        for row in c.fetchall():
            name, description, schedule, max_participants = row
            c.execute("SELECT email FROM participants WHERE activity_name=?", (name,))
            participants = [r[0] for r in c.fetchall()]
            activities[name] = {
                "description": description,
                "schedule": schedule,
                "max_participants": max_participants,
                "participants": participants
            }
        return activities

def add_activity(activity: dict):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO activities (name, description, schedule, max_participants) VALUES (?, ?, ?, ?)",
                  (activity["name"], activity["description"], activity["schedule"], activity["max_participants"]))
        conn.commit()

def add_participant(activity_name: str, email: str):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO participants (activity_name, email) VALUES (?, ?)", (activity_name, email))
        conn.commit()

def remove_participant(activity_name: str, email: str):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM participants WHERE activity_name=? AND email=?", (activity_name, email))
        conn.commit()
