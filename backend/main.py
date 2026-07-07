from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json, os

from services.gemini_service import (
    chat_with_bharat_mitra, analyze_civic_issue, recommend_schemes
)
from services.complaint_service import (
    file_complaint, track_complaint, list_all_complaints
)

app = FastAPI(title="Smart Bharat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load schemes
with open("data/schemes.json") as f:
    SCHEMES = json.load(f)


class ChatRequest(BaseModel):
    message: str
    history: list = []


class ProfileRequest(BaseModel):
    age: int
    gender: str
    occupation: str
    income: int
    state: str


@app.get("/")
def root():
    return {"message": "🇮🇳 Smart Bharat API is running!"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    reply = chat_with_bharat_mitra(req.message, req.history)
    return {"reply": reply}


@app.post("/api/report-issue")
async def report_issue(
    user_name: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...)
):
    image_bytes = await image.read()
    ai_result = analyze_civic_issue(image_bytes, description)
    complaint = file_complaint(user_name, "auto", description, location, ai_result)
    return {"complaint": complaint, "ai_analysis": ai_result}


@app.get("/api/complaint/{cid}")
def get_complaint(cid: str):
    return track_complaint(cid)


@app.get("/api/complaints")
def all_complaints():
    return list_all_complaints()


@app.post("/api/recommend-schemes")
def recommend(profile: ProfileRequest):
    result = recommend_schemes(profile.dict(), SCHEMES)
    return {"recommendations": result}


@app.get("/api/schemes")
def get_schemes():
    return SCHEMES


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)