"""
Urology Conditions Matrix
Urinary, prostate, kidney, and reproductive system conditions
Based on clinical symptom matrix - 1 = symptom present for this condition
"""

# Urology symptom matrix with weighted relationships
UROLOGY_SYMPTOM_MATRIX = {
    "uti": {
        "name": "Urinary Tract Infection",
        "symptoms": [
            {"id": "frequency", "label": "Frequent urination", "weight": 0.9},
            {"id": "urgency", "label": "Urgency to urinate", "weight": 0.9},
            {"id": "nocturia", "label": "Waking to urinate at night", "weight": 0.7},
            {"id": "pain_burning", "label": "Pain/burning on urination", "weight": 0.95},
            {"id": "recurrent_utis", "label": "History of recurrent UTIs", "weight": 0.8}
        ],
        "investigations": ["needs_urine_dipstick"],
        "pattern": "Acute onset frequency, urgency, dysuria. More common in women."
    },
    
    "overactive_bladder": {
        "name": "Overactive Bladder",
        "symptoms": [
            {"id": "frequency", "label": "Frequent urination", "weight": 0.9},
            {"id": "urgency", "label": "Sudden strong urge", "weight": 0.95},
            {"id": "nocturia", "label": "Waking to urinate at night", "weight": 0.8}
        ],
        "investigations": [],
        "pattern": "Chronic urgency and frequency without infection. Often behavioral triggers."
    },
    
    "bph": {
        "name": "Benign Prostatic Hyperplasia (BPH)",
        "symptoms": [
            {"id": "frequency", "label": "Frequent urination", "weight": 0.85},
            {"id": "urgency", "label": "Urgency to urinate", "weight": 0.8},
            {"id": "weak_stream", "label": "Weak urine stream", "weight": 0.95},
            {"id": "incomplete_emptying", "label": "Feeling of incomplete emptying", "weight": 0.9},
            {"id": "intermittency", "label": "Stop-start urination", "weight": 0.85},
            {"id": "straining", "label": "Straining to urinate", "weight": 0.9},
            {"id": "nocturia", "label": "Frequent nighttime urination", "weight": 0.9}
        ],
        "investigations": ["needs_psa", "needs_prostate_exam"],
        "pattern": "Progressive obstructive symptoms in men >50. Gradual onset."
    },
    
    "prostate_cancer": {
        "name": "Prostate Cancer",
        "symptoms": [
            {"id": "frequency", "label": "Frequent urination", "weight": 0.6},
            {"id": "urgency", "label": "Urgency to urinate", "weight": 0.6},
            {"id": "weak_stream", "label": "Weak urine stream", "weight": 0.75},
            {"id": "incomplete_emptying", "label": "Incomplete emptying", "weight": 0.7},
            {"id": "intermittency", "label": "Stop-start urination", "weight": 0.6},
            {"id": "straining", "label": "Straining to urinate", "weight": 0.65},
            {"id": "nocturia", "label": "Nocturia", "weight": 0.7},
            {"id": "blood_in_urine", "label": "Blood in urine", "weight": 0.75},
            {"id": "family_history_prostate_cancer", "label": "Family history of prostate cancer", "weight": 0.95}
        ],
        "investigations": ["needs_psa", "needs_prostate_exam"],
        "pattern": "Often asymptomatic early. Similar to BPH but risk factors important."
    },
    
    "interstitial_cystitis": {
        "name": "Interstitial Cystitis / Painful Bladder Syndrome",
        "symptoms": [
            {"id": "frequency", "label": "Frequent urination", "weight": 0.9},
            {"id": "urgency", "label": "Urgency", "weight": 0.85},
            {"id": "nocturia", "label": "Nocturia", "weight": 0.8},
            {"id": "pain_burning", "label": "Bladder pain/burning", "weight": 0.95},
            {"id": "blood_in_urine", "label": "Blood in urine", "weight": 0.6},
            {"id": "severe_pain", "label": "Severe pain", "weight": 0.9},
            {"id": "pelvic_pain", "label": "Pelvic pain", "weight": 0.95}
        ],
        "investigations": ["needs_cystoscopy"],
        "pattern": "Chronic pelvic pain, pressure, discomfort with bladder filling. Dietary triggers."
    },
    
    "kidney_stones": {
        "name": "Kidney Stones (Renal Calculi)",
        "symptoms": [
            {"id": "blood_in_urine", "label": "Blood in urine", "weight": 0.9},
            {"id": "severe_pain", "label": "Severe flank/back pain", "weight": 0.98},
            {"id": "pelvic_pain", "label": "Pelvic pain", "weight": 0.85}
        ],
        "investigations": ["needs_ct_kidney_ureter_bladder"],
        "pattern": "Sudden severe colicky pain, restless, hematuria. Comes in waves."
    },
    
    "bladder_cancer": {
        "name": "Bladder Cancer",
        "symptoms": [
            {"id": "urgency", "label": "Urgency", "weight": 0.7},
            {"id": "blood_in_urine", "label": "Painless blood in urine", "weight": 0.98}
        ],
        "investigations": ["needs_urinary_cytology", "needs_cystoscopy", "needs_ct_kidney_ureter_bladder"],
        "pattern": "Painless visible hematuria is hallmark. Smoking is major risk factor."
    },
    
    "vaginal_atrophy": {
        "name": "Vaginal Atrophy (Atrophic Vaginitis)",
        "symptoms": [
            {"id": "recurrent_utis", "label": "Recurrent UTIs", "weight": 0.95},
            {"id": "vaginal_changes", "label": "Vaginal dryness/irritation", "weight": 0.9}
        ],
        "investigations": [],
        "pattern": "Post-menopausal women. Vaginal dryness, recurrent UTIs, dyspareunia."
    },
    
    "prostatitis": {
        "name": "Prostatitis",
        "symptoms": [
            {"id": "frequency", "label": "Frequency", "weight": 0.85},
            {"id": "urgency", "label": "Urgency", "weight": 0.85},
            {"id": "weak_stream", "label": "Weak stream", "weight": 0.75},
            {"id": "incomplete_emptying", "label": "Incomplete emptying", "weight": 0.75},
            {"id": "intermittency", "label": "Intermittency", "weight": 0.7},
            {"id": "straining", "label": "Straining", "weight": 0.75},
            {"id": "nocturia", "label": "Nocturia", "weight": 0.8},
            {"id": "pain_burning", "label": "Painful urination", "weight": 0.9},
            {"id": "severe_pain", "label": "Severe pain", "weight": 0.85},
            {"id": "pelvic_pain", "label": "Pelvic/perineal pain", "weight": 0.95}
        ],
        "investigations": ["needs_prostate_exam", "needs_urine_dipstick"],
        "pattern": "Acute bacterial: sudden onset pain, fever. Chronic: persistent pelvic pain."
    },
    
    "appendicitis": {
        "name": "Appendicitis (mimics urological pain)",
        "symptoms": [
            {"id": "severe_pain", "label": "Severe pain", "weight": 0.95},
            {"id": "pain_right_lower", "label": "Right lower quadrant pain", "weight": 0.98},
            {"id": "bowel_symptoms", "label": "Nausea/vomiting", "weight": 0.85}
        ],
        "investigations": [],
        "pattern": "Starts periumbilical, migrates to RLQ. Rebound tenderness. SURGICAL EMERGENCY."
    },
    
    "sti": {
        "name": "Sexually Transmitted Infection",
        "symptoms": [
            {"id": "pain_burning", "label": "Painful urination", "weight": 0.85},
            {"id": "pelvic_pain", "label": "Pelvic pain", "weight": 0.75},
            {"id": "swelling", "label": "Genital swelling/sores", "weight": 0.9},
            {"id": "discharge", "label": "Urethral/vaginal discharge", "weight": 0.95}
        ],
        "investigations": ["see_sexual_health_clinic"],
        "pattern": "Discharge, dysuria, pelvic pain. Recent unprotected sex."
    },
    
    "testicular_torsion": {
        "name": "Testicular Torsion",
        "symptoms": [
            {"id": "severe_pain", "label": "Sudden severe testicular pain", "weight": 0.98},
            {"id": "pelvic_pain", "label": "Pelvic/groin pain", "weight": 0.85},
            {"id": "swelling", "label": "Testicular swelling", "weight": 0.95},
            {"id": "very_tender", "label": "Extremely tender to touch", "weight": 0.98}
        ],
        "investigations": ["needs_testicular_exam"],
        "pattern": "SURGICAL EMERGENCY. Sudden severe pain, high-riding testis, absent cremaster reflex."
    },
    
    "testicular_cancer": {
        "name": "Testicular Cancer",
        "symptoms": [
            {"id": "swelling", "label": "Painless testicular lump/swelling", "weight": 0.98},
            {"id": "heavy_periods", "label": "Feeling of heaviness", "weight": 0.75},
            {"id": "irregular_testicular_texture", "label": "Irregular testicular texture", "weight": 0.95}
        ],
        "investigations": ["needs_testicular_exam"],
        "pattern": "Painless lump in testicle. Young men 15-35. Urgent referral needed."
    }
}


def calculate_urology_probability(condition_id: str, symptom_scores: dict) -> float:
    """
    Calculate probability of urological condition
    
    Args:
        condition_id: Condition identifier
        symptom_scores: Dict of symptom scores {symptom_id: 0-10}
        
    Returns:
        Probability 0-1
    """
    condition = UROLOGY_SYMPTOM_MATRIX.get(condition_id)
    if not condition:
        return 0.0
    
    total_weight = 0.0
    weighted_score = 0.0
    
    for symptom in condition["symptoms"]:
        symptom_id = symptom["id"]
        weight = symptom["weight"]
        score = symptom_scores.get(symptom_id, 0) / 10.0
        
        weighted_score += score * weight
        total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    return min(1.0, weighted_score / total_weight)


def get_required_investigations(condition_id: str) -> list[str]:
    """Get required investigations for a condition"""
    condition = UROLOGY_SYMPTOM_MATRIX.get(condition_id)
    if not condition:
        return []
    return condition.get("investigations", [])
