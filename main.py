from fastapi import FastAPI
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import requests
from fastapi import UploadFile, File

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

# ---------------- JWT CONFIG ----------------

SECRET_KEY = "edunexus_secret_key"
ALGORITHM = "HS256"

# ---------------- SAMPLE DATA ----------------

courses = [
    {"id": 1, "title": "Python Basics", "is_premium": False},
    {"id": 2, "title": "Django Fundamentals", "is_premium": True},
    {"id": 3, "title": "FastAPI Mastery", "is_premium": True}
]

lessons = [
    {"id": 1, "course_id": 1, "title": "Intro to Python"},
    {"id": 2, "course_id": 1, "title": "Python Variables"}
]

enrollments = []
users = []
subscriptions = []
payments = []

plans = [
    {"id": 1, "name": "Basic", "price": 500, "duration": 30},
    {"id": 2, "name": "Pro", "price": 1000, "duration": 60},
    {"id": 3, "name": "Enterprise", "price": 2000, "duration": 90}
]

def has_active_subscription(username):
    return any(sub["username"] == username for sub in subscriptions)

# ---------------- BASIC ----------------

@app.get("/")
def home():
    return {"message": "EduNexus API Running"}

# ---------------- COURSES ----------------

@app.get("/courses")
def get_courses():
    return courses

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    return next((c for c in courses if c["id"] == course_id), {"error": "Not found"})

@app.get("/lessons/{course_id}")
def get_lessons(course_id: int):
    return [l for l in lessons if l["course_id"] == course_id]

@app.post("/enroll/{course_id}")
def enroll(course_id: int):
    enrollments.append({"course_id": course_id})
    return {"message": "Enrolled"}

@app.get("/my-courses")
def my_courses():
    return enrollments

# ---------------- AUTH ----------------

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/auth/register")
def register(user: UserRegister):
    users.append(user.dict())
    return {"message": "Registered"}

@app.post("/auth/login")
def login(user: UserLogin):
    for u in users:
        if u["username"] == user.username and u["password"] == user.password:
            token = jwt.encode(
                {"username": user.username, "exp": datetime.utcnow() + timedelta(hours=1)},
                SECRET_KEY,
                algorithm=ALGORITHM
            )
            return {"access_token": token}
    return {"error": "Invalid"}

# ---------------- PLANS ----------------

@app.get("/plans")
def get_plans():
    return plans

class SubscribeRequest(BaseModel):
    username: str
    plan_id: int

@app.post("/subscribe")
def subscribe(req: SubscribeRequest):
    plan = next((p for p in plans if p["id"] == req.plan_id), None)
    if not plan:
        return {"error": "Plan not found"}

    subscriptions.append({"username": req.username, "plan": plan["name"]})
    payments.append({"username": req.username, "amount": plan["price"]})

    return {"message": "Subscribed"}

@app.get("/payments/{username}")
def payments_user(username: str):
    return [p for p in payments if p["username"] == username]

# ---------------- RECOMMEND ----------------

@app.get("/recommend/{username}")
def recommend(username: str):
    access = has_active_subscription(username)
    return [c for c in courses if access or not c["is_premium"]]

# ---------------- EXTRA APIs (IMPORTANT) ----------------

@app.get("/analytics")
def analytics():
    return {
        "total_users": len(users),
        "total_courses": len(courses),
        "revenue": sum(p["amount"] for p in payments)
    }

@app.get("/notifications")
def notifications():
    return [
        {"message": "Course enrolled"},
        {"message": "Lesson completed"}
    ]

@app.get("/activity")
def activity():
    return [
        {"user": "Subha", "action": "Enrolled Course"},
        {"user": "Subha", "action": "Completed Lesson"}
    ]


@app.get("/activity")
def activity():
    return [
        {"user": "Subha", "action": "Enrolled Course"},
    ]
@app.websocket("/ws/chat/{room}")
async def chat(websocket: WebSocket, room: str):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()

        print("RECEIVED:", data)

        user, message = data.split("|")

        await websocket.send_json({
            "user": user,
            "message": message
        })


@app.websocket("/ws/chat/general")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        print("RECEIVED:", data)

        await websocket.send_text(data)       