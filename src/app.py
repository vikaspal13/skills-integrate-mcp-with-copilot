"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""


from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from db import (
    init_db,
    get_all_activities,
    add_participant,
    remove_participant
)
from seed_db import seed_db


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")


# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize the database on startup
@app.on_event("startup")
def on_startup():
    init_db()
    seed_db()




@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")



@app.get("/activities")
def get_activities():
    return get_all_activities()



@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activities = get_all_activities()
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email in activities[activity_name]["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")
    if len(activities[activity_name]["participants"]) >= activities[activity_name]["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    add_participant(activity_name, email)
    return {"message": f"Signed up {email} for {activity_name}"}



@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    activities = get_all_activities()
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email not in activities[activity_name]["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
    remove_participant(activity_name, email)
    return {"message": f"Unregistered {email} from {activity_name}"}
