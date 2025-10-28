"""
Clinical Context and Educational Content
Provides interpretation guidance, clinical pearls, and teaching points for differential diagnosis results
"""

CLINICAL_CONCEPTS = {
    "bacterial_infections": {
        "title": "Understanding Bacterial Infections",
        "key_points": [
            "Bacteria are all around us and some help ensure the normal functioning of the human body",
            "Some bacteria can colonise parts of the body but not cause infection",
            "Different bacteria attack different areas of the body",
            "Local and systemic effects and immune responses form the basis of symptomatology",
            "Bacterial infections can be fatal or have serious long term complications if left untreated",
            "Genetics provide bacterial immunity which reduces with age and depression",
            "There is no way apart from antibiotics to treat bacterial infections",
            "Should be done carefully (even very unwell) to prevent complications and transmission to vulnerable people",
            "Holistic therapies or remedies should not delay seeking antibiotics where appropriate"
        ]
    }
}

ESSENTIAL_QUESTIONS = {
    "bacterial_vs_viral": {
        "question": "Is the ill person glum, generally weary, not interacting or behaving usually?",
        "interpretation": "This could mean a bacterial as opposed to a viral infection",
        "clinical_significance": "Bacterial infections typically cause more systemic malaise"
    },
    "upper_vs_lower_respiratory": {
        "question": "Sneezing or coughing?",
        "interpretation": "Sneezing is used to clear the upper airways and coughing is to clear the lower airway",
        "clinical_significance": "Helps localize the infection"
    },
    "seasonal_triggers": {
        "question": "Are the symptoms seasonal or environmentally triggered with any family or personal history of atopy?",
        "interpretation": "Consider allergic rhinitis or environmental triggers",
        "clinical_significance": "May not be infectious at all"
    },
    "red_flags": {
        "question": "If unable to swallow, difficulty breathing, confusion, dehydration or fits",
        "interpretation": "Needs immediate medical review",
        "clinical_significance": "Emergency red flags requiring urgent care"
    }
}

CLINICAL_PEARLS = {
    "swollen_glands": {
        "bacterial": "Bacteria get trapped in the glands or lymph nodes in the neck and make them tender (tender with cancer) and very swollen (not very swollen with viral illness)",
        "viral": "Glands may be palpable but not as tender or large"
    },
    "tonsillitis": {
        "bacterial": "Bacterial tonsillitis can have pus (a strain of strep pyogenes = pus forming) but may not",
        "note": "Pus presence increases likelihood but absence doesn't rule out bacterial"
    },
    "strep_contact": {
        "question": "Has there been a contact with strep case (even a carrier with a new strain)?",
        "significance": "Increases pre-test probability of strep infection"
    },
    "culture": {
        "question": "Has a culture been done for checking resistance to antibiotics?",
        "note": "Important for treatment failures or recurrent infections"
    }
}

SYMPTOM_CONTEXT = {
    "sore_throat": {
        "viral_causes": [
            "Viral pharyngitis",
            "Post nasal drip from coughing",
            "Allergic rhinitis (with clear mucous)",
            "Rhinosinusitis (AKA a cold)"
        ],
        "when_to_suspect_bacterial": [
            "Glum, generally weary",
            "Not interacting normally",
            "Very tender swollen glands",
            "Pus on tonsils",
            "No cough"
        ]
    },
    "cough": {
        "triggers": "Coughing can be triggered by swelling from sinusitis or general inflammation",
        "treatment_options": [
            "Nasal steroid may benefit sinusitis with post nasal drip",
            "Eustachian tube dysfunction"
        ],
        "red_flag": "Persistent cough >3 weeks needs review"
    },
    "neck_pain": {
        "with_body_ache": "With all over body ache it could be flu",
        "localized": "Fluid and ibuprofen along with paracetamol should be used",
        "clearing_throat": "Sore neck from clearing throat with covid post nasal drip is common",
        "red_flag": "Severe unilateral neck pain or unable to move neck"
    },
    "vomiting": {
        "triggers": [
            "Gagging on phlegm",
            "Swelling in the tonsils",
            "General inflammation which may also cause headache or body ache"
        ],
        "timeframe": "Earache over 2 days should trigger GP review",
        "note": "Vomiting with severe headache is a red flag"
    }
}

PRIORITIES = {
    "secondary": "Ask questions to ensure no sinister pathology requiring medical review",
    "primary": "Aim to suggest appropriate symptom relief",
    "tertiary": "Give interesting relevant information if secondary and primary goals complete"
}


def get_clinical_context(condition: str = None, symptom: str = None) -> dict:
    """
    Get relevant clinical context for a condition or symptom
    
    Args:
        condition: Condition name (e.g. 'bacterial_infections')
        symptom: Symptom name (e.g. 'sore_throat', 'cough')
        
    Returns:
        Dict with relevant clinical context
    """
    context = {}
    
    if condition and condition in CLINICAL_CONCEPTS:
        context["concept"] = CLINICAL_CONCEPTS[condition]
    
    if symptom and symptom in SYMPTOM_CONTEXT:
        context["symptom_guidance"] = SYMPTOM_CONTEXT[symptom]
    
    context["essential_questions"] = ESSENTIAL_QUESTIONS
    context["clinical_pearls"] = CLINICAL_PEARLS
    context["priorities"] = PRIORITIES
    
    return context


def get_interpretation_guidance(symptoms: list[str]) -> str:
    """
    Generate interpretation guidance based on symptoms
    
    Args:
        symptoms: List of symptoms
        
    Returns:
        String with interpretation guidance
    """
    guidance = []
    
    # Check for specific symptom patterns
    if any(s in ["sore throat", "throat pain", "sore_throat"] for s in symptoms):
        guidance.append("Sore Throat Context:")
        guidance.append("- Could be viral pharyngitis, post-nasal drip, or allergic rhinitis")
        guidance.append("- Bacterial more likely if: very tender glands, pus, no cough, systemically unwell")
    
    if any(s in ["cough", "coughing"] for s in symptoms):
        guidance.append("\nCough Context:")
        guidance.append("- Can be triggered by sinusitis or general inflammation")
        guidance.append("- Consider nasal steroid for post-nasal drip")
    
    if any(s in ["headache", "neck pain", "body ache"] for s in symptoms):
        guidance.append("\nPain Context:")
        guidance.append("- Body aches with fever suggest flu")
        guidance.append("- Use paracetamol and ibuprofen together")
        guidance.append("- Ensure adequate fluids")
    
    # Add general guidance
    guidance.append("\nKey Differentiating Questions:")
    guidance.append("1. Is patient glum/weary/not interacting normally? (suggests bacterial)")
    guidance.append("2. Sneezing (upper respiratory) vs coughing (lower respiratory)?")
    guidance.append("3. Any seasonal pattern or allergy history?")
    guidance.append("4. Recent contact with confirmed strep case?")
    
    return "\n".join(guidance)
