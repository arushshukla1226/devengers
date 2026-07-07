import json
import os
from typing import Any, List

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

from services.complaint_service import file_complaint, list_all_complaints, track_complaint
from services.gemini_service import analyze_civic_issue, chat_with_bharat_mitra, recommend_schemes

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Smart Bharat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load schemes using absolute path (required for Vercel serverless)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data", "schemes.json"), encoding="utf-8") as f:
    SCHEMES: List[Any] = json.load(f)

# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    history: List[Any] = []  # explicit List avoids mutable-default-arg lint warning


class ProfileRequest(BaseModel):
    age: int
    gender: str
    occupation: str
    income: int
    state: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/")
def root() -> dict:
    return {"message": "🇮🇳 Smart Bharat API is running!"}


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    reply = chat_with_bharat_mitra(req.message, req.history)
    return {"reply": reply}


@app.post("/api/report-issue")
async def report_issue(
    user_name: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...),
) -> dict:
    image_bytes = await image.read()
    ai_result = analyze_civic_issue(image_bytes, description)
    complaint = file_complaint(user_name, "auto", description, location, ai_result)
    return {"complaint": complaint, "ai_analysis": ai_result}


@app.get("/api/complaint/{cid}")
def get_complaint(cid: str) -> dict:
    return track_complaint(cid)


@app.get("/api/complaints")
def all_complaints() -> list:
    return list_all_complaints()


@app.post("/api/recommend-schemes")
def recommend(profile: ProfileRequest) -> dict:
    result = recommend_schemes(profile.model_dump(), SCHEMES)
    return {"recommendations": result}


@app.get("/api/schemes")
def get_schemes() -> list:
    return SCHEMES


# ---------------------------------------------------------------------------
# Vercel serverless handler
# ---------------------------------------------------------------------------

handler = Mangum(app, lifespan="off")

# ---------------------------------------------------------------------------
# Local development entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)