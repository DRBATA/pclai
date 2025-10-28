"""
Pain Conditions Symptom Matrix
Defines symptoms and their relationships to musculoskeletal pain conditions
"""

# Symptom matrix for pain-related conditions
PAIN_SYMPTOM_MATRIX = {
    "rheumatoid_arthritis": {
        "name": "Rheumatoid Arthritis",
        "symptoms": [
            {"id": "joint_pain", "label": "Joint Pain", "weight": 0.9},
            {"id": "swelling", "label": "Swelling", "weight": 0.85},
            {"id": "stiffness", "label": "Stiffness (especially morning)", "weight": 0.9},
            {"id": "redness", "label": "Redness", "weight": 0.6},
            {"id": "warmth", "label": "Warmth", "weight": 0.7},
            {"id": "deformity", "label": "Joint Deformity", "weight": 0.8},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.75},
            {"id": "fatigue", "label": "Fatigue", "weight": 0.7},
            {"id": "fever", "label": "Fever", "weight": 0.5},
            {"id": "weight_loss", "label": "Weight Loss", "weight": 0.5},
            {"id": "nodules", "label": "Nodules", "weight": 0.8}
        ],
        "typical_pattern": "Symmetrical small joints, morning stiffness >30min, systemic symptoms"
    },
    "osteoarthritis": {
        "name": "Osteoarthritis",
        "symptoms": [
            {"id": "joint_pain", "label": "Joint Pain", "weight": 0.9},
            {"id": "swelling", "label": "Swelling", "weight": 0.6},
            {"id": "stiffness", "label": "Stiffness (worse with activity)", "weight": 0.8},
            {"id": "deformity", "label": "Joint Deformity", "weight": 0.7},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.8},
            {"id": "bone_pain", "label": "Bone Pain", "weight": 0.6}
        ],
        "typical_pattern": "Asymmetrical large/weight-bearing joints, worse end of day, no systemic features"
    },
    "gout": {
        "name": "Gout",
        "symptoms": [
            {"id": "joint_pain", "label": "Severe Joint Pain", "weight": 0.95},
            {"id": "swelling", "label": "Swelling", "weight": 0.9},
            {"id": "stiffness", "label": "Stiffness", "weight": 0.7},
            {"id": "redness", "label": "Redness", "weight": 0.9},
            {"id": "warmth", "label": "Warmth", "weight": 0.9},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.8},
            {"id": "fever", "label": "Fever", "weight": 0.6}
        ],
        "typical_pattern": "Acute onset, big toe typical, severe pain, red hot swollen joint"
    },
    "sprain": {
        "name": "Sprain/Strain",
        "symptoms": [
            {"id": "joint_pain", "label": "Joint Pain", "weight": 0.85},
            {"id": "swelling", "label": "Swelling", "weight": 0.8},
            {"id": "stiffness", "label": "Stiffness", "weight": 0.7},
            {"id": "redness", "label": "Redness", "weight": 0.5},
            {"id": "warmth", "label": "Warmth", "weight": 0.5},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.8}
        ],
        "typical_pattern": "Recent injury, localized pain, improves with rest"
    },
    "fracture": {
        "name": "Fracture",
        "symptoms": [
            {"id": "joint_pain", "label": "Severe Pain", "weight": 0.95},
            {"id": "swelling", "label": "Swelling", "weight": 0.9},
            {"id": "redness", "label": "Redness", "weight": 0.6},
            {"id": "warmth", "label": "Warmth", "weight": 0.6},
            {"id": "deformity", "label": "Visible Deformity", "weight": 0.9},
            {"id": "limited_range", "label": "Unable to Use/Move", "weight": 0.95},
            {"id": "bone_pain", "label": "Bone Pain", "weight": 0.95}
        ],
        "typical_pattern": "Trauma, deformity, unable to bear weight, point tenderness"
    },
    "tendinitis": {
        "name": "Tendinitis",
        "symptoms": [
            {"id": "joint_pain", "label": "Pain Near Joint", "weight": 0.85},
            {"id": "swelling", "label": "Swelling", "weight": 0.6},
            {"id": "stiffness", "label": "Stiffness", "weight": 0.7},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.75}
        ],
        "typical_pattern": "Overuse injury, pain with movement, tender along tendon"
    },
    "bursitis": {
        "name": "Bursitis",
        "symptoms": [
            {"id": "joint_pain", "label": "Joint Pain", "weight": 0.8},
            {"id": "swelling", "label": "Localized Swelling", "weight": 0.85},
            {"id": "stiffness", "label": "Stiffness", "weight": 0.7},
            {"id": "redness", "label": "Redness", "weight": 0.6},
            {"id": "warmth", "label": "Warmth", "weight": 0.7},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.7}
        ],
        "typical_pattern": "Fluid-filled swelling, worse with pressure, near joints"
    },
    "fibromyalgia": {
        "name": "Fibromyalgia",
        "symptoms": [
            {"id": "widespread_pain", "label": "Widespread Pain", "weight": 0.95},
            {"id": "stiffness", "label": "Stiffness", "weight": 0.8},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.6},
            {"id": "fatigue", "label": "Severe Fatigue", "weight": 0.9},
            {"id": "sleep_problems", "label": "Sleep Problems", "weight": 0.85},
            {"id": "cognitive_issues", "label": "Brain Fog", "weight": 0.7},
            {"id": "muscle_weakness", "label": "Muscle Weakness", "weight": 0.6}
        ],
        "typical_pattern": "Chronic widespread pain, tender points, fatigue, sleep issues"
    },
    "carpal_tunnel": {
        "name": "Carpal Tunnel Syndrome",
        "symptoms": [
            {"id": "hand_pain", "label": "Hand/Wrist Pain", "weight": 0.8},
            {"id": "stiffness", "label": "Stiffness", "weight": 0.6},
            {"id": "limited_range", "label": "Limited Range of Motion", "weight": 0.7},
            {"id": "muscle_weakness", "label": "Hand Weakness", "weight": 0.85},
            {"id": "numbness_tingling", "label": "Numbness/Tingling", "weight": 0.95}
        ],
        "typical_pattern": "Numbness thumb/index/middle fingers, worse at night, weakness grip"
    }
}


def get_condition_symptoms(condition_id: str) -> dict:
    """Get symptom list for a specific condition"""
    return PAIN_SYMPTOM_MATRIX.get(condition_id, {})


def calculate_condition_probability(condition_id: str, symptom_scores: dict) -> float:
    """
    Calculate probability of a condition based on symptom scores (0-10)
    
    Args:
        condition_id: ID of the condition
        symptom_scores: Dict of {symptom_id: score} where score is 0-10
        
    Returns:
        Probability score 0-1
    """
    condition = PAIN_SYMPTOM_MATRIX.get(condition_id)
    if not condition:
        return 0.0
    
    total_weight = 0.0
    weighted_score = 0.0
    
    for symptom in condition["symptoms"]:
        symptom_id = symptom["id"]
        weight = symptom["weight"]
        score = symptom_scores.get(symptom_id, 0) / 10.0  # Normalize to 0-1
        
        weighted_score += score * weight
        total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    return min(1.0, weighted_score / total_weight)


def get_all_conditions() -> list:
    """Get list of all pain conditions"""
    return [
        {"id": k, "name": v["name"], "pattern": v["typical_pattern"]}
        for k, v in PAIN_SYMPTOM_MATRIX.items()
    ]
