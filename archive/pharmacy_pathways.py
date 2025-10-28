"""
UK Pharmacy First Pathways
Conditions that can be managed by community pharmacists with specific criteria
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

class PharmacyPathwayResult(BaseModel):
    eligible: bool
    condition: str
    reason: Optional[str] = None
    recommended_action: str
    medications: List[str] = []
    contraindication_warnings: List[str] = []
    red_flags: List[str] = []


# Pharmacy pathway eligibility criteria
PHARMACY_PATHWAYS = {
    "uti": {
        "name": "Uncomplicated Urinary Tract Infection (UTI)",
        "inclusion_criteria": {
            "age_min": 16,
            "age_max": 64,
            "gender": ["Female"],  # Typically only women for uncomplicated UTI
            "required_symptoms": ["painful_urination", "frequent_urination"],
            "duration_max_days": 3
        },
        "exclusion_criteria": {
            "red_flags": [
                "blood_in_urine",
                "severe_abdominal_pain",
                "loin_pain",
                "fever_over_38",
                "vomiting",
                "signs_of_sepsis"
            ],
            "contraindications": [
                "pregnant",
                "catheter",
                "immunosuppressed",
                "kidney_disease",
                "recurrent_uti_3plus",
                "male"  # Males need GP referral
            ]
        },
        "medications": [
            {
                "name": "Nitrofurantoin 100mg",
                "duration": "3 days",
                "contraindications": ["kidney_disease", "liver_disease", "g6pd_deficiency"],
                "advice": "Take with food. Complete full course. Urine may turn dark yellow/brown."
            },
            {
                "name": "Trimethoprim 200mg",
                "duration": "3 days",
                "contraindications": ["pregnancy", "folate_deficiency", "blood_disorder"],
                "advice": "Complete full course even if symptoms improve."
            }
        ]
    },
    
    "shingles": {
        "name": "Shingles (Herpes Zoster)",
        "inclusion_criteria": {
            "age_min": 18,
            "required_symptoms": ["painful_rash", "blisters", "unilateral_distribution"],
            "duration_max_days": 3  # Within 72 hours of rash onset
        },
        "exclusion_criteria": {
            "red_flags": [
                "eye_involvement",
                "facial_rash_near_eye",
                "widespread_rash",
                "immunosuppressed",
                "severe_pain",
                "secondary_infection"
            ],
            "contraindications": [
                "pregnant",
                "breastfeeding",
                "immunosuppressed",
                "kidney_disease"
            ]
        },
        "medications": [
            {
                "name": "Aciclovir 800mg",
                "duration": "7 days, 5 times daily",
                "contraindications": ["kidney_disease", "dehydration"],
                "advice": "Start within 72 hours of rash. Drink plenty of fluids. Avoid contact with pregnant women and babies."
            }
        ]
    },
    
    "impetigo": {
        "name": "Impetigo",
        "inclusion_criteria": {
            "age_min": 1,
            "required_symptoms": ["crusty_sores", "golden_crust", "spreading_rash"],
            "localized": True
        },
        "exclusion_criteria": {
            "red_flags": [
                "widespread_lesions",
                "bullous_impetigo",
                "cellulitis",
                "fever",
                "systemically_unwell"
            ],
            "contraindications": [
                "newborn",
                "immunosuppressed",
                "eczema_severe"
            ]
        },
        "medications": [
            {
                "name": "Fusidic acid cream 2%",
                "duration": "7 days",
                "contraindications": [],
                "advice": "Apply 3-4 times daily. Wash hands before and after. Avoid sharing towels."
            }
        ]
    },
    
    "insect_bite": {
        "name": "Infected Insect Bite",
        "inclusion_criteria": {
            "age_min": 1,
            "required_symptoms": ["localized_redness", "swelling", "warmth"],
            "duration_max_days": 7
        },
        "exclusion_criteria": {
            "red_flags": [
                "spreading_cellulitis",
                "red_streaks",
                "fever",
                "lymphangitis",
                "systemically_unwell"
            ],
            "contraindications": [
                "immunosuppressed",
                "diabetes_uncontrolled",
                "peripheral_vascular_disease"
            ]
        },
        "medications": [
            {
                "name": "Flucloxacillin 500mg",
                "duration": "7 days",
                "contraindications": ["penicillin_allergy"],
                "advice": "Take on empty stomach (1 hour before or 2 hours after food)."
            }
        ]
    },
    
    "sore_throat": {
        "name": "Sore Throat (FeverPAIN ≥ 4 or Centor ≥ 3)",
        "inclusion_criteria": {
            "age_min": 5,
            "required_symptoms": ["sore_throat"],
            "fever_pain_score_min": 4  # Or Centor >= 3
        },
        "exclusion_criteria": {
            "red_flags": [
                "unable_to_swallow",
                "drooling",
                "stridor",
                "severe_systemic_illness",
                "unilateral_swelling",
                "peritonsillar_abscess",
                "scarlet_fever_rash"
            ],
            "contraindications": [
                "penicillin_allergy",
                "glandular_fever_suspected",
                "immunosuppressed"
            ]
        },
        "medications": [
            {
                "name": "Phenoxymethylpenicillin (Penicillin V) 500mg",
                "duration": "5-10 days",
                "contraindications": ["penicillin_allergy"],
                "advice": "Take 4 times daily. Complete full course."
            }
        ]
    },
    
    "sinusitis": {
        "name": "Acute Sinusitis",
        "inclusion_criteria": {
            "age_min": 12,
            "required_symptoms": ["facial_pain", "nasal_discharge"],
            "duration_min_days": 10  # Symptoms for >10 days without improvement
        },
        "exclusion_criteria": {
            "red_flags": [
                "severe_frontal_headache",
                "swelling_around_eyes",
                "visual_disturbance",
                "severe_unilateral_pain",
                "signs_of_sepsis",
                "immunosuppressed"
            ],
            "contraindications": [
                "immunosuppressed",
                "cystic_fibrosis",
                "recent_sinus_surgery"
            ]
        },
        "medications": [
            {
                "name": "Phenoxymethylpenicillin 500mg",
                "duration": "5 days",
                "contraindications": ["penicillin_allergy"],
                "advice": "Most sinusitis resolves without antibiotics. Use if symptoms >10 days."
            }
        ]
    },
    
    "otitis_media": {
        "name": "Acute Otitis Media (Ear Infection)",
        "inclusion_criteria": {
            "age_min": 1,
            "age_max": 17,
            "required_symptoms": ["ear_pain", "bulging_eardrum_or_discharge"],
            "bilateral_or_systemically_unwell": True
        },
        "exclusion_criteria": {
            "red_flags": [
                "mastoiditis",
                "facial_nerve_palsy",
                "meningitis_signs",
                "systemically_very_unwell",
                "immunosuppressed",
                "cleft_palate",
                "down_syndrome",
                "cochlear_implant"
            ],
            "contraindications": [
                "penicillin_allergy",
                "immunosuppressed",
                "perforation_chronic"
            ]
        },
        "medications": [
            {
                "name": "Amoxicillin 500mg",
                "duration": "5-7 days",
                "contraindications": ["penicillin_allergy"],
                "advice": "Most resolve without antibiotics. Use if bilateral, discharge, or systemically unwell."
            }
        ]
    }
}


def check_pharmacy_eligibility(
    condition: str,
    age: int,
    gender: str,
    symptoms: List[str],
    red_flags: List[str],
    contraindications: List[str],
    duration_days: Optional[int] = None,
    pregnant: bool = False
) -> PharmacyPathwayResult:
    """
    Check if patient is eligible for pharmacy pathway
    
    Args:
        condition: Condition ID (e.g. 'uti', 'shingles')
        age: Patient age
        gender: Patient gender ('Male', 'Female', 'Other')
        symptoms: List of symptoms present
        red_flags: List of red flag symptoms present
        contraindications: List of medical contraindications
        duration_days: Duration of symptoms in days
        pregnant: Is patient pregnant
        
    Returns:
        PharmacyPathwayResult with eligibility and recommendations
    """
    pathway = PHARMACY_PATHWAYS.get(condition.lower())
    if not pathway:
        return PharmacyPathwayResult(
            eligible=False,
            condition=condition,
            reason="Condition not in pharmacy pathway scheme",
            recommended_action="Consult GP"
        )
    
    inclusion = pathway["inclusion_criteria"]
    exclusion = pathway["exclusion_criteria"]
    
    # Check age
    if age < inclusion.get("age_min", 0):
        return PharmacyPathwayResult(
            eligible=False,
            condition=pathway["name"],
            reason=f"Patient too young (minimum age {inclusion['age_min']})",
            recommended_action="Consult GP or pediatrician"
        )
    
    if "age_max" in inclusion and age > inclusion["age_max"]:
        return PharmacyPathwayResult(
            eligible=False,
            condition=pathway["name"],
            reason=f"Patient over maximum age ({inclusion['age_max']})",
            recommended_action="Consult GP"
        )
    
    # Check gender (for UTI)
    if "gender" in inclusion and gender not in inclusion["gender"]:
        return PharmacyPathwayResult(
            eligible=False,
            condition=pathway["name"],
            reason=f"Pathway only available for {', '.join(inclusion['gender'])}",
            recommended_action="Consult GP"
        )
    
    # Check duration
    if duration_days:
        if "duration_max_days" in inclusion and duration_days > inclusion["duration_max_days"]:
            return PharmacyPathwayResult(
                eligible=False,
                condition=pathway["name"],
                reason=f"Symptoms present too long (max {inclusion['duration_max_days']} days for pharmacy pathway)",
                recommended_action="Consult GP"
            )
        
        if "duration_min_days" in inclusion and duration_days < inclusion["duration_min_days"]:
            return PharmacyPathwayResult(
                eligible=False,
                condition=pathway["name"],
                reason=f"Too early for antibiotic (wait minimum {inclusion['duration_min_days']} days)",
                recommended_action="Self-care and review if not improving"
            )
    
    # Check red flags
    present_red_flags = [rf for rf in red_flags if rf in exclusion["red_flags"]]
    if present_red_flags:
        severity = "Call 999" if any(rf in ["signs_of_sepsis", "stridor", "severe_systemic_illness"] for rf in present_red_flags) else "Go to A&E or urgent GP"
        return PharmacyPathwayResult(
            eligible=False,
            condition=pathway["name"],
            reason="Red flag symptoms present",
            recommended_action=severity,
            red_flags=present_red_flags
        )
    
    # Check contraindications
    if pregnant and "pregnant" in exclusion["contraindications"]:
        return PharmacyPathwayResult(
            eligible=False,
            condition=pathway["name"],
            reason="Pregnancy is a contraindication for this pathway",
            recommended_action="Consult GP"
        )
    
    present_contraindications = [c for c in contraindications if c in exclusion["contraindications"]]
    if present_contraindications:
        return PharmacyPathwayResult(
            eligible=False,
            condition=pathway["name"],
            reason="Medical contraindications present",
            recommended_action="Consult GP",
            contraindication_warnings=present_contraindications
        )
    
    # Check required symptoms
    required_symptoms = inclusion.get("required_symptoms", [])
    missing_symptoms = [s for s in required_symptoms if s not in symptoms]
    if missing_symptoms:
        return PharmacyPathwayResult(
            eligible=False,
            condition=pathway["name"],
            reason=f"Missing typical symptoms: {', '.join(missing_symptoms)}",
            recommended_action="May not be this condition - consult GP"
        )
    
    # ELIGIBLE!
    safe_medications = []
    warnings = []
    
    for med in pathway["medications"]:
        med_contraindications = [c for c in contraindications if c in med["contraindications"]]
        if not med_contraindications:
            safe_medications.append(f"{med['name']} ({med['duration']})")
        else:
            warnings.append(f"{med['name']}: Not suitable due to {', '.join(med_contraindications)}")
    
    return PharmacyPathwayResult(
        eligible=True,
        condition=pathway["name"],
        recommended_action="Eligible for Pharmacy First pathway - visit community pharmacist",
        medications=safe_medications,
        contraindication_warnings=warnings
    )
