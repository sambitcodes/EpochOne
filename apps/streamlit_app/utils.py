import os
import streamlit as st
import math

def get_api_base():
    """Get API base URL from env or secrets."""
    # Check Docker-specific env var first, then standard env var, then secrets
    return os.getenv("DOCKER_API_BASE_URL") or os.getenv("API_BASE_URL") or st.secrets.get("API_BASE_URL", "http://localhost:8000")

def kg_to_lbs(kg): return round(kg * 2.20462, 1)
def lbs_to_kg(lbs): return round(lbs / 2.20462, 1)
def cm_to_in(cm): return round(cm / 2.54, 1)
def in_to_cm(inches): return round(inches * 2.54, 1)

def ft_in_to_cm(ft, inches):
    total_inches = (ft * 12) + inches
    return round(total_inches * 2.54, 1)

def cm_to_ft_in(cm):
    total_inches = cm / 2.54
    ft = int(total_inches // 12)
    inches = round(total_inches % 12, 1)
    return ft, inches

def calculate_metrics(weight, height, age, gender, lifestyle, waist, neck, hip=None):
    """Calculate derived metrics. Assumes METRIC input (kg, cm)."""
    metrics = {}
    
    # BMI
    height_m = height / 100
    if height_m > 0:
        metrics["bmi"] = round(weight / (height_m ** 2), 1)
    else:
        metrics["bmi"] = 0
    
    # Body Fat % (Navy Seal)
    try:
        if gender.lower() == "male":
            metrics["body_fat"] = round(495 / (1.0324 - 0.19077 * math.log10(max(1, waist - neck)) + 0.15456 * math.log10(max(1, height))) - 450, 1)
        else:
            # female formula needs hip
            hip_calc = hip or waist + 10 # fallback
            metrics["body_fat"] = round(495 / (1.29579 - 0.35004 * math.log10(max(1, waist + hip_calc - neck)) + 0.22100 * math.log10(max(1, height))) - 450, 1)
    except:
        metrics["body_fat"] = None
        
    # Lean Body Mass
    if metrics.get("body_fat") is not None:
        metrics["lbm"] = round(weight * (1 - metrics["body_fat"]/100), 1)
    else:
        metrics["lbm"] = None
        
    # Maintenance Calories (Mifflin-St Jeor)
    if gender.lower() == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "active": 1.55,
        "very_active": 1.725
    }
    metrics["maintenance"] = int(bmr * multipliers.get(lifestyle.lower().replace(" ", "_"), 1.2))
    
    return metrics
