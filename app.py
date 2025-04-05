# app.py - Main FastAPI application file
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from datetime import datetime
import logging
from model import PetTrainingAssistant, load_pet_breed_model
from utils import preprocess_text, extract_image_features, get_training_recommendations, create_training_plan, analyze_behavior_video

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Pet Training Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mock user database
mock_users_db = {"user1@example.com": {"password": "pass123", "id": "user1"}}

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Data models
class PetProfile(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[str] = None
    behavior_notes: Optional[str] = None
    owner_id: Optional[str] = None

class TrainingProgress(BaseModel):
    pet_id: str
    focus_area: str
    skills_mastered: List[str]
    overall_progress: float

class UserQuery(BaseModel):
    message: str
    pet_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class TrainingRecommendation(BaseModel):
    title: str
    description: str
    difficulty: str
    techniques: List[str]
    frequency: str
    age_adjustment: str

class HealthRecord(BaseModel):
    pet_id: str
    weight: float
    vaccination_status: str
    last_vet_visit: str
    notes: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    token: str

class TrainingPlanRequest(BaseModel):
    pet_id: str
    focus_area: str
    pet_profile: PetProfile

# Mock session storage
sessions: Dict[str, Dict] = {}

# Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.info(f"Received token: {token}")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return sessions[token]["user_id"]

# Initialize models
training_assistant = None
pet_breed_model = None

try:
    training_assistant = PetTrainingAssistant()
    logger.info("Training assistant loaded successfully")
except Exception as e:
    logger.error(f"Error loading training assistant: {e}")

try:
    pet_breed_model = load_pet_breed_model()
    logger.info("Pet breed model loaded successfully")
except Exception as e:
    logger.error(f"Error loading pet breed model: {e}")

# Routes
@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    if user.email in mock_users_db and mock_users_db[user.email]["password"] == user.password:
        session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        sessions[session_id] = {"user_id": mock_users_db[user.email]["id"], "timestamp": datetime.now().isoformat()}
        logger.info(f"Login successful, token: {session_id}")
        return {"token": session_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/profile")
async def create_or_update_profile(profile: PetProfile, current_user: str = Depends(get_current_user)):
    profile.owner_id = current_user
    return {"id": "pet_" + datetime.now().strftime("%Y%m%d%H%M%S"), **profile.dict()}

@app.post("/training/progress")
async def update_training_progress(progress: TrainingProgress, current_user: str = Depends(get_current_user)):
    return {"status": "success", "progress": progress.dict()}

@app.post("/chat")
async def chat(query: UserQuery, current_user: str = Depends(get_current_user)):
    if not training_assistant:
        raise HTTPException(status_code=503, detail="Training assistant model not available")
    processed_text = preprocess_text(query.message)
    context = query.context or {"user_id": current_user}
    response = training_assistant.generate_response(processed_text, context)
    return {"response": response, "timestamp": datetime.now().isoformat()}

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...), pet_id: Optional[str] = Form(None), current_user: str = Depends(get_current_user)):
    temp_filename = f"temp_{file.filename}"
    try:
        contents = await file.read()
        with open(temp_filename, "wb") as f:
            f.write(contents)
        features = extract_image_features(temp_filename)
        breed_results = {"species": "Dog", "breed": "Labrador Retriever", "confidence": 0.92}
        recommendations = get_training_recommendations(breed_results["breed"], pet_id=pet_id)
        return {
            "analysis": {
                "breed_detection": breed_results,
                "behavior_assessment": {"energy_level": "High", "attention_span": "Moderate", "trainability": "High"}
            },
            "recommendations": recommendations
        }
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/analyze/video")
async def analyze_video(file: UploadFile = File(...), pet_id: Optional[str] = Form(None), current_user: str = Depends(get_current_user)):
    temp_filename = f"temp_{file.filename}"
    try:
        contents = await file.read()
        with open(temp_filename, "wb") as f:
            f.write(contents)
        analysis = analyze_behavior_video(temp_filename)
        return {"analysis": analysis, "timestamp": datetime.now().isoformat()}
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/training/plan")
async def get_training_plan(request: TrainingPlanRequest, current_user: str = Depends(get_current_user)):
    plan = create_training_plan(request.pet_profile, request.focus_area)
    return {"training_plan": plan, "pet_id": request.pet_id}

@app.post("/recommendations")
async def get_recommendations(pet_id: str = Form(...), focus_area: str = Form(...), current_user: str = Depends(get_current_user)):
    recommendations = get_training_recommendations("Labrador Retriever", pet_id=pet_id)
    return {"recommendations": recommendations}

@app.post("/health/record")
async def record_health_info(health: HealthRecord, current_user: str = Depends(get_current_user)):
    return {"status": "success", "health_record": health.dict()}

@app.get("/socialization/tips")
async def get_socialization_tips(pet_id: str, current_user: str = Depends(get_current_user)):
    tips = ["Introduce your pet to new people gradually.", "Use positive reinforcement for good interactions."]
    return {"tips": tips}

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)