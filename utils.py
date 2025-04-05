# utils.py - Utility functions for the Pet Training Assistant
import re
import numpy as np
import os

def preprocess_text(text):
    """Preprocess text for NLP tasks"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.strip()

def extract_image_features(image_path, model=None):
    """Mock image feature extraction"""
    return np.zeros((1, 1280))

def get_training_recommendations(breed, features=None, pet_age="adult", behaviors=None):
    """Get training recommendations based on breed and other factors"""
    default_recommendations = [
        {"title": "Basic Obedience", "description": "Essential commands", "techniques": ["Sit", "Stay"], "difficulty": "Beginner", "frequency": "Daily, 5-10 mins"}
    ]
    breed_recommendations = {
        "Labrador Retriever": [
            {"title": "Retrieval Games", "description": "Use their retrieving instincts", "techniques": ["Fetch"], "difficulty": "Beginner", "frequency": "2-3 times/week"}
        ]
    }
    recommendations = breed_recommendations.get(breed, default_recommendations)
    age_adjustments = {
        "puppy": "Short 5-min sessions",
        "adult": "10-15 min sessions",
        "senior": "Gentle 5-10 min sessions"
    }
    for rec in recommendations:
        rec["age_adjustment"] = age_adjustments.get(pet_age.lower(), age_adjustments["adult"])
    return recommendations

def create_training_plan(pet_profile, focus_area):
    """Create a customized training plan based on pet profile and focus area"""
    if hasattr(pet_profile, 'dict'):
        pet_profile = pet_profile.dict()
    plan = {
        "pet_name": pet_profile.get("name", "your pet"),
        "focus_area": focus_area,
        "duration": "2 weeks",
        "daily_sessions": [
            {
                "day": 1,
                "exercises": [{"name": "Introduction", "duration": "5 mins", "steps": ["Start with basics"]}]
            }
        ],
        "progress_tracking": {"metrics": ["Consistency"], "milestones": ["Basic response"]}
    }
    return plan

def analyze_behavior_video(video_path):
    """Analyze a video of pet behavior"""
    return {
        "duration": "00:35",
        "behaviors_observed": [{"behavior": "Jumping up", "frequency": "3 times", "context": "When excited"}],
        "recommendations": ["Practice 'sit' to manage jumping"]
    }