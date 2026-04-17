from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from bson import ObjectId
from jose import jwt, JWTError

from database import users, notes
from auth import hash_password, verify_password, create_token

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# ---------- MODELS ----------
class User(BaseModel):
    username: str
    password: str

class Note(BaseModel):
    note: str


# ---------- AUTH ----------
def get_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------- AUTH APIs ----------
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "API working"
    }
@app.post("/signup")
def signup(user: User):
    if users.find_one({"username": user.username}):
        return {"error": "User exists"}

    users.insert_one({
        "username": user.username,
        "password": hash_password(user.password)
    })

    return {"message": "Signup success"}


@app.post("/login")
def login(user: User):
    db_user = users.find_one({"username": user.username})

    if not db_user:
        return {"error": "User not found"}

    if not verify_password(user.password, db_user["password"]):
        return {"error": "Wrong password"}

    token = create_token({
        "user_id": str(db_user["_id"]),
        "username": db_user["username"]
    })

    return {"access_token": token, "token_type": "bearer"}


# ---------- NOTES CRUD ----------
@app.post("/notes")
def add_note(note: Note, user_id: str = Depends(get_user)):
    notes.insert_one({
        "note": note.note,
        "user_id": user_id
    })
    return {"message": "Note added"}


@app.get("/notes")
def get_notes(user_id: str = Depends(get_user)):
    data = notes.find({"user_id": user_id})

    return [
        {"id": str(n["_id"]), "note": n["note"]}
        for n in data
    ]


@app.delete("/notes/{id}")
def delete_note(id: str, user_id: str = Depends(get_user)):
    notes.delete_one({"_id": ObjectId(id), "user_id": user_id})
    return {"message": "Deleted"}