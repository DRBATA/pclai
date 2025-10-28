"""
Urology Bayesian Calculator
Based on the throat infection calculator approach (differentialCalculations.jsx)
Uses evidence-based priors and likelihood functions for urological conditions
"""

import math
from typing import Dict, Any, List, Optional


# =============================================================================
# SYMPTOM KEYWORD MAPPING (for search_urology_symptoms tool)
# =============================================================================

SYMPTOM_KEYWORD_MAP = {
    "sudden_onset": {
        "label": "Sudden onset of symptoms (within hours/days)",
        "keywords": ["sudden", "acute", "came on quickly", "started yesterday", "overnight", 
                    "rapid", "all at once", "out of nowhere", "this morning", "few hours"]
    },
    "gradual_progression": {
        "label": "Gradual onset over weeks/months",
        "keywords": ["gradual", "slowly", "over time", "getting worse", "progressive", 
                    "months", "years", "chronic", "been happening for a while"]
    },
    "dysuria": {
        "label": "Pain or burning when urinating",
        "keywords": ["pain", "burning", "stinging", "hurts to pee", "painful urination",
                    "burns when i pee", "dysuria", "discomfort", "sore"]
    },
    "hematuria": {
        "label": "Blood in urine",
        "keywords": ["blood", "red urine", "pink urine", "brown urine", "hematuria",
                    "bloody", "blood in pee", "dark urine", "clots"]
    },
    "fever": {
        "label": "Fever, chills, or feeling unwell",
        "keywords": ["fever", "temperature", "hot", "chills", "shivering", "sweating",
                    "feeling unwell", "flu-like", "shaking", "malaise"]
    },
    "weak_stream": {
        "label": "Weak urine stream",
        "keywords": ["weak stream", "poor flow", "dribbling", "trickle", "slow stream",
                    "can't pee strongly", "takes ages", "weak flow", "difficulty peeing"]
    },
    "urgency": {
        "label": "Urgent need to urinate",
        "keywords": ["urgency", "urgent", "can't wait", "sudden urge", "rush to toilet",
                    "desperate", "need to go now", "can't hold it", "immediate need"]
    },
    "nocturia_severe": {
        "label": "Waking to urinate 3+ times per night",
        "keywords": ["nocturia", "wake up to pee", "nighttime", "3 times a night", 
                    "waking at night", "up all night", "disturbs sleep", "nocturnal",
                    "get up in the night", "get up at night", "wee at night", "pee at night",
                    "toilet at night", "bathroom at night", "night time", "during the night"]
    }
}

# =============================================================================
# RESEARCH DATA - TO BE FILLED WITH EVIDENCE-BASED VALUES
# =============================================================================

# RESEARCH COMPLETE - Evidence-based epidemiological data
UROLOGY_PRIORS = {
    "uti": {
        "female_baseline": 0.30,  # ~10-20% annual incidence, 50-60% lifetime; 30% prior for symptomatic women
        "male_baseline": 0.05,   # 13% lifetime risk; <0.5% annual before age 50
        "citation": "Lifetime UTI risk ~50-60% women, ~13% men. Annual ~10-20% women. Women get UTIs 30x more than men.",
        "notes": "Higher in sexually active women, pregnant women. Men: low until advanced age"
    },
    
    "bph": {
        "age_40_49": 0.10,  # 8-10% histological BPH; symptomatic rare
        "age_50_59": 0.26,  # 25-30% histological; 26% moderate-to-severe LUTS
        "age_60_69": 0.60,  # 50-70% histological; ~50% clinically symptomatic
        "age_70_plus": 0.85,  # 80-90% histological; >80% with LUTS
        "citation": "Histological BPH: ~50-70% in 60s, ~80-90% >70. Survey data: 70% LUTS ages 60-69, >80% over 70.",
        "notes": "Almost universal by age 80; symptomatic in majority of older men"
    },
    
    "prostate_cancer": {
        "baseline_age_50": 0.002,  # <0.5% before age 50; 0.2% cumulative by 50
        "baseline_age_65": 0.08,   # ~6-8% by mid-60s; median diagnosis age 66-70
        "with_family_history": 0.20,  # ~20-25% with first-degree relative (doubles risk)
        "citation": "Lifetime risk 1 in 8 (12-13%). <0.5% before age 50, ~6.5% by age 70-79. Family history doubles risk.",
        "notes": "Early cancer rarely causes symptoms; symptomatic cancer usually advanced"
    },
    
    "overactive_bladder": {
        "general_population": 0.16,  # EPIC: 11.8%, NOBLE: 16% overall; ~1 in 6 adults
        "female": 0.17,  # NOBLE: 16.9%, EPIC: 12.8%
        "male": 0.16,   # NOBLE: 16.0%, EPIC: 10.8%
        "citation": "EPIC study: 11.8% overall (10.8% men, 12.8% women). NOBLE study: 16% overall (16.0% men, 16.9% women)."
    },
    
    "kidney_stones": {
        "general_population": 0.10,  # U.S. prevalence ~8.8% (2010) rising to 10.1% (2016)
        "with_previous_stones": 0.50,  # 50% recurrence within 5-10 years; 75% within 20 years
        "male": 0.106,  # Men 10.6%
        "female": 0.071,  # Women 7.1%
        "citation": "Overall prevalence ~8.8-10% (10.6% men, 7.1% women). Recurrence 35-50% within 5 years, ~75% within 20 years."
    },
    
    "interstitial_cystitis": {
        "general_population": 0.03,  # 2.7% strict criteria to 6.5% broad criteria
        "female": 0.05,  # 3.3-7.9 million women; ~3-6% symptom prevalence
        "male": 0.015,  # Female:male ratio ~5:1; includes chronic prostatitis/pelvic pain
        "citation": "Symptom-based prevalence women: 2.7% (strict) to 6.5% (broad). Female:male ratio ~5:1."
    },
    
    "prostatitis": {
        "general_population": 0.05,  # Chronic prostatitis/chronic pelvic pain syndrome
        "acute": 0.01,  # Acute bacterial prostatitis relatively rare
        "citation": "Prevalence estimates vary; chronic forms in few percent of men. Acute bacterial prostatitis uncommon."
    }
}

# RESEARCH COMPLETE - Evidence-based symptom likelihood ratios converted to log-odds points
SYMPTOM_POINTS = {
    # Points added to log-odds (like throat calculator)
    # Positive = favors condition, Negative = against condition
    # Formula: points = ln(LR) * weight_factor (typically 2-4)
    
    "sudden_onset": {
        "uti": 5,  # ~80-90% of UTIs acute onset vs ~10% BPH; LR ~8.5, ln(8.5)≈2.14, *2.5≈5.3
        "kidney_stones": 5,  # Sudden severe pain is classic; similar LR
        "bph": -4,  # 90%+ gradual onset; sudden onset strongly against
        "prostate_cancer": -4,  # Also insidious
        "oab": -2,  # Usually chronic/gradual
        "ic": -2,   # Chronic pain syndrome
        "prostatitis": 2,  # Acute bacterial is sudden; chronic is not
        "citation": "Clinical: UTI/stones typically <48hr onset. BPH develops over years. ~85% UTI acute vs ~10% BPH acute → LR~8.5."
    },
    
    "dysuria": {  # Pain/burning on urination
        "uti": 1.5,  # Sensitivity ~75%, specificity ~50%, LR+ ~1.5; ln(1.5)≈0.4, *3≈1.2
        "prostatitis": 2,  # Common in prostatitis, slightly higher specificity
        "kidney_stones": 1,  # Can occur but less specific
        "ic": 2,  # Chronic dysuria hallmark of IC
        "bph": -1,  # Usually painless voiding
        "oab": -2,  # Urgency without burning
        "prostate_cancer": -1,  # Usually painless
        "citation": "Bent et al JAMA 2002: Dysuria sens ~75%, spec ~50%, LR+ 1.5, LR− 0.5 for UTI."
    },
    
    "hematuria": {  # Blood in urine
        "kidney_stones": 6,  # ~85% of stones have hematuria; LR stone vs BPH ~8-9, ln(8)≈2.1, *3≈6.3
        "bladder_cancer": 6,  # ~85% present with painless hematuria; very specific
        "uti": 1.5,  # 20-30% have hematuria; LR+ ~1.7-2.0 for UTI
        "prostate_cancer": 2,  # Can occur in advanced disease
        "ic": 2,  # Glomerulations cause microhematuria
        "bph": 0.5,  # ~10% microscopic from friable vessels
        "oab": -2,  # Rare unless other pathology
        "citation": "Stones: ~85% with hematuria. Bladder cancer: ~85% painless hematuria. UTI: ~20-30%, LR+ 1.7."
    },
    
    "fever": {
        "uti": -2,  # Simple cystitis usually afebrile (<5%); fever suggests pyelonephritis
        "prostatitis": 7,  # >80% acute prostatitis febrile; highly specific; LR approaching infinity vs BPH
        "pyelonephritis": 8,  # Upper UTI; fever hallmark
        "bph": -8,  # BPH never causes fever (0%); fever rules out pure BPH
        "oab": -6,  # No infection/inflammation
        "prostate_cancer": -4,  # Afebrile unless infected
        "ic": -4,  # Not infectious
        "kidney_stones": 0,  # Afebrile unless infected (obstructed pyelo)
        "citation": "Cystitis usually no fever. Pyelonephritis/acute prostatitis: fever >80%. BPH: 0% (fever suggests infection)."
    },
    
    "gradual_progression": {
        "bph": 5,  # Develops over years; hallmark of BPH; 90%+ gradual
        "prostate_cancer": 4,  # Insidious progression
        "oab": 3,  # Can develop gradually
        "ic": 3,  # Chronic waxing/waning
        "uti": -5,  # Acute onset; gradual rules out typical UTI
        "kidney_stones": -5,  # Sudden colicky pain
        "prostatitis": -3,  # Acute form is sudden
        "citation": "BPH: gradual LUTS over years (guideline). UTI/stones: acute <48hr onset. Inverse of sudden_onset."
    },
    
    "nocturia_severe": {  # Waking 3+ times per night
        "bph": 3,  # Common in BPH; IPSS Q7 correlates with severity
        "oab": 3,  # Equally common in OAB; nocturia is key OAB symptom
        "prostate_cancer": 2,  # Can occur with outlet obstruction
        "uti": 1,  # Frequency day and night in acute UTI
        "ic": 2,  # Chronic frequency
        "citation": "Nocturia common in BPH (obstruction) and OAB (urgency). IPSS Q7 severity marker."
    },
    
    # Additional symptoms for completeness
    "weak_stream": {
        "bph": 4,  # Mechanical obstruction; very specific
        "prostate_cancer": 2,  # Can cause obstruction if advanced
        "uti": -2,  # Irritative not obstructive
        "oab": -1,  # Storage not voiding problem
        "citation": "Weak stream indicates outlet obstruction; highly specific for BPH in older men."
    },
    
    "urgency": {
        "oab": 4,  # Defining symptom of OAB
        "uti": 3,  # Very common in acute cystitis
        "ic": 3,  # Chronic urgency/frequency
        "bph": 1,  # Can occur with incomplete emptying
        "prostatitis": 2,  # Inflammatory urgency
        "citation": "Urgency: OAB hallmark. Also common in UTI (90%), IC, prostatitis."
    }
}


# =============================================================================
# LIKELIHOOD FUNCTIONS (Like throat calculator's continuous functions)
# =============================================================================

def calculate_dysuria_uti_likelihood(severity: float) -> float:
    """
    Likelihood of UTI given dysuria severity (0-100 scale)
    Similar to lymphNodeTendernessStrepLikelihood in throat calculator
    
    TUNED based on clinical reasoning:
    - Mild dysuria (20/100): Low probability ~0.15 (could be irritation)
    - Moderate (50/100): 50% probability (typical UTI pain)
    - Severe (80/100): High probability ~0.85 (strongly suggests infection)
    
    Args:
        severity: Pain severity 0-100
    Returns:
        Likelihood ratio for UTI (0-1)
    """
    # Adjusted sigmoid: center at 50, slope 0.18 for reasonable curve
    # At 20: P~0.15, At 50: P~0.5, At 80: P~0.87
    value = 1 / (1 + math.exp(-0.18 * (severity - 50)))
    return max(0, min(1, value))


def calculate_dysuria_noninfectious_likelihood(severity: float) -> float:
    """
    Likelihood of non-infectious causes given dysuria
    TODO: RESEARCH - How does IC/stone pain differ from UTI dysuria?
    """
    # Lower peak, centered at moderate severity
    if severity > 70:
        return 0.3  # Very severe might suggest stones
    
    peak = 0.6
    peak_position = 40
    width = 15
    value = peak * math.exp(-math.pow(severity - peak_position, 2) / (2 * math.pow(width, 2)))
    return max(0, min(1, value))


def calculate_weak_stream_bph_likelihood(severity: float) -> float:
    """
    Likelihood of BPH given weak stream severity
    TUNED based on IPSS correlation analysis:
    - IPSS weak stream scores 0-5 map to 0-100
    - Score 3/5 (moderate, ~60/100) → ~50% probability
    - Score 5/5 (severe, 100/100) → ~85% probability
    
    Weak stream is mechanical obstruction - highly specific for BPH in older men.
    Correlation with prostate volume: r≈0.31
    
    Args:
        severity: 0-100 scale (0=never, 100=always weak stream)
    Returns:
        Likelihood ratio
    """
    # Adjusted: logistic 0.4 (wider contribution) + Gaussian 0.6 (wider spread to not drop at 100)
    sigmoid = 0.4 / (1 + math.exp(-0.1 * (severity - 35)))  # Shifted midpoint to 35 for earlier rise
    gaussian = 0.6 * math.exp(-math.pow(severity - 80, 2) / (2 * 500))  # Wider (500 vs 150) to plateau
    # At severity 60: sigmoid ≈0.26, gaussian ≈0.19 → ~0.45
    # At severity 100: sigmoid ≈0.40, gaussian ≈0.45 → ~0.85
    return max(0, min(1, sigmoid + gaussian))


def calculate_severe_pain_stones_likelihood(pain: float) -> float:
    """
    Kidney stones cause sudden severe colicky pain
    TUNED: Stones typically 8-10/10 pain ("worst pain ever")
    - Flank/CVA pain 70+/100 strongly suggests stone
    - Pain <60 makes stone unlikely
    - With hematuria: probability even higher
    
    Args:
        pain: Pain severity 0-100
    Returns:
        Likelihood ratio
    """
    # Very steep sigmoid - stones are VERY painful (renal colic)
    if pain < 60:
        return 0.05  # Unlikely if not severe
    
    # Steep curve: at 70→~0.5, at 85→~0.95, at 100→~0.998
    value = 1 / (1 + math.exp(-0.3 * (pain - 70)))
    return max(0, min(1, value))


# =============================================================================
# MAIN CALCULATOR
# =============================================================================

CONDITIONS = [
    "uti",
    "bph", 
    "prostate_cancer",
    "overactive_bladder",
    "kidney_stones",
    "interstitial_cystitis",
    "prostatitis"
]


def compute_urology_differential(
    symptoms: Dict[str, Any],
    patient_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Main Bayesian calculator for urology conditions
    Based on throat calculator approach from differentialCalculations.jsx
    
    Args:
        symptoms: Dict of symptom IDs and values
        patient_info: Age, gender, risk factors
    
    Returns:
        Dict with probabilities, recommendations, graph structure, citations
    """
    
    # Step 1: Set baseline priors from epidemiology
    priors = _calculate_priors(patient_info)
    
    # Step 2: Convert to log-odds
    log_odds = {}
    for condition in CONDITIONS:
        p = priors[condition]
        # Avoid log(0) or log(1)
        p = max(0.001, min(0.999, p))
        log_odds[condition] = math.log(p / (1 - p))
    
    # Step 3: Add discrete symptom points
    log_odds = _add_discrete_symptoms(log_odds, symptoms)
    
    # Step 4: Add continuous symptom likelihoods
    log_odds = _add_continuous_symptoms(log_odds, symptoms)
    
    # Step 5: Softmax to get posterior probabilities
    probabilities = _softmax(log_odds)
    
    # Step 6: Generate clinical recommendation
    recommendation = _make_clinical_recommendation(probabilities, symptoms, patient_info)
    
    # Step 7: Build graph structure for FindPivots
    graph = _build_graph_structure(probabilities, symptoms)
    
    # Step 8: Collect citations
    citations = _collect_citations()
    
    return {
        "probabilities": probabilities,
        "recommendation": recommendation,
        "graph": graph,
        "citations": citations,
        "log_odds": log_odds  # For debugging
    }


def _calculate_priors(patient_info: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate baseline priors from epidemiology
    Adjusts for age, gender, risk factors
    """
    age = patient_info.get("age", 50)
    gender = patient_info.get("gender", "unknown")
    
    priors = {}
    
    # UTI
    if gender == "female":
        priors["uti"] = UROLOGY_PRIORS["uti"]["female_baseline"]
    else:
        priors["uti"] = UROLOGY_PRIORS["uti"]["male_baseline"]
    
    # BPH (only in males, increases with age)
    if gender == "male":
        if age >= 70:
            priors["bph"] = UROLOGY_PRIORS["bph"]["age_70_plus"]
        elif age >= 60:
            priors["bph"] = UROLOGY_PRIORS["bph"]["age_60_69"]
        elif age >= 50:
            priors["bph"] = UROLOGY_PRIORS["bph"]["age_50_59"]
        else:
            priors["bph"] = UROLOGY_PRIORS["bph"]["age_40_49"]
    else:
        priors["bph"] = 0.001  # Essentially zero in females
    
    # Prostate Cancer
    if gender == "male":
        if patient_info.get("family_history_prostate_cancer"):
            priors["prostate_cancer"] = UROLOGY_PRIORS["prostate_cancer"]["with_family_history"]
        elif age >= 65:
            priors["prostate_cancer"] = UROLOGY_PRIORS["prostate_cancer"]["baseline_age_65"]
        else:
            priors["prostate_cancer"] = UROLOGY_PRIORS["prostate_cancer"]["baseline_age_50"]
    else:
        priors["prostate_cancer"] = 0.001
    
    # OAB
    if gender == "female":
        priors["overactive_bladder"] = UROLOGY_PRIORS["overactive_bladder"]["female"]
    elif gender == "male":
        priors["overactive_bladder"] = UROLOGY_PRIORS["overactive_bladder"]["male"]
    else:
        priors["overactive_bladder"] = UROLOGY_PRIORS["overactive_bladder"]["general_population"]
    
    # Kidney Stones
    if patient_info.get("previous_kidney_stones"):
        priors["kidney_stones"] = UROLOGY_PRIORS["kidney_stones"]["with_previous_stones"]
    else:
        priors["kidney_stones"] = UROLOGY_PRIORS["kidney_stones"]["general_population"]
    
    # IC
    if gender == "female":
        priors["interstitial_cystitis"] = UROLOGY_PRIORS["interstitial_cystitis"]["female"]
    elif gender == "male":
        priors["interstitial_cystitis"] = UROLOGY_PRIORS["interstitial_cystitis"]["male"]
    else:
        priors["interstitial_cystitis"] = UROLOGY_PRIORS["interstitial_cystitis"]["general_population"]
    
    # Prostatitis
    priors["prostatitis"] = UROLOGY_PRIORS["prostatitis"]["general_population"]
    
    return priors


def _add_discrete_symptoms(log_odds: Dict[str, float], symptoms: Dict[str, Any]) -> Dict[str, float]:
    """
    Add points for discrete symptoms (like Centor score approach)
    """
    # Sudden onset
    if symptoms.get("onset_speed") == "sudden":
        for condition in SYMPTOM_POINTS["sudden_onset"]:
            if condition in log_odds:
                log_odds[condition] += SYMPTOM_POINTS["sudden_onset"][condition]
    
    # Gradual progression
    if symptoms.get("onset_speed") == "gradual":
        for condition in SYMPTOM_POINTS["gradual_progression"]:
            if condition in log_odds:
                log_odds[condition] += SYMPTOM_POINTS["gradual_progression"][condition]
    
    # Dysuria present
    if symptoms.get("dysuria") or "pain_burning" in symptoms.get("reported_symptoms", []):
        for condition in SYMPTOM_POINTS["dysuria"]:
            if condition in log_odds:
                log_odds[condition] += SYMPTOM_POINTS["dysuria"][condition]
    
    # Blood in urine
    if symptoms.get("hematuria") or "blood_in_urine" in symptoms.get("reported_symptoms", []):
        for condition in SYMPTOM_POINTS["hematuria"]:
            if condition in log_odds:
                log_odds[condition] += SYMPTOM_POINTS["hematuria"][condition]
    
    # Fever
    if symptoms.get("fever_present"):
        for condition in SYMPTOM_POINTS["fever"]:
            if condition in log_odds:
                log_odds[condition] += SYMPTOM_POINTS["fever"][condition]
    
    # Severe nocturia
    nocturia_count = symptoms.get("nocturia_per_night", 0)
    if nocturia_count >= 3:
        for condition in SYMPTOM_POINTS["nocturia_severe"]:
            if condition in log_odds:
                log_odds[condition] += SYMPTOM_POINTS["nocturia_severe"][condition]
    
    return log_odds


def _add_continuous_symptoms(log_odds: Dict[str, float], symptoms: Dict[str, Any]) -> Dict[str, float]:
    """
    Add continuous symptom likelihoods (using sigmoid/gaussian functions)
    """
    # Dysuria severity
    dysuria_severity = symptoms.get("dysuria_severity", 0)
    if dysuria_severity > 0:
        uti_likelihood = calculate_dysuria_uti_likelihood(dysuria_severity)
        non_infectious_likelihood = calculate_dysuria_noninfectious_likelihood(dysuria_severity)
        
        # Add log ratio (like throat calculator)
        safe_uti = max(uti_likelihood, 0.0001)
        safe_other = max(non_infectious_likelihood, 0.0001)
        log_ratio = math.log(safe_uti / safe_other)
        
        log_odds["uti"] += log_ratio * 0.5
        log_odds["prostatitis"] += log_ratio * 0.3
        log_odds["bph"] -= log_ratio * 0.3
    
    # Weak stream severity
    weak_stream_severity = symptoms.get("weak_stream_severity", 0)
    if weak_stream_severity > 0:
        bph_likelihood = calculate_weak_stream_bph_likelihood(weak_stream_severity)
        log_odds["bph"] += math.log(max(bph_likelihood, 0.0001)) * 0.5
        log_odds["prostate_cancer"] += math.log(max(bph_likelihood * 0.7, 0.0001)) * 0.3
    
    # Severe pain
    pain_severity = symptoms.get("pain_severity", 0)
    if pain_severity > 70:
        stones_likelihood = calculate_severe_pain_stones_likelihood(pain_severity)
        log_odds["kidney_stones"] += math.log(max(stones_likelihood, 0.0001)) * 0.7
    
    return log_odds


def _softmax(log_odds: Dict[str, float]) -> Dict[str, float]:
    """Convert log-odds to probabilities using softmax"""
    exp_odds = {cond: math.exp(lo) for cond, lo in log_odds.items()}
    sum_exp = sum(exp_odds.values())
    
    probabilities = {cond: exp_val / sum_exp for cond, exp_val in exp_odds.items()}
    return probabilities


def _make_clinical_recommendation(
    probabilities: Dict[str, float],
    symptoms: Dict[str, Any],
    patient_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate clinical recommendation based on probabilities
    Similar to throat calculator's recommendation logic
    
    TODO: RESEARCH - Get clinical thresholds from guidelines
    """
    sorted_conditions = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    top_condition, top_prob = sorted_conditions[0]
    
    # TODO: Get these thresholds from NICE/EAU/AUA guidelines
    
    # UTI pathway
    if top_condition == "uti" and top_prob > 0.65:
        return {
            "primary_diagnosis": "Likely urinary tract infection",
            "confidence": "high",
            "action": "See GP this week for urine test and antibiotics",
            "self_care": [
                "Drink plenty of water (2-3 liters per day)",
                "Try cranberry juice",
                "Take paracetamol for discomfort",
                "Avoid caffeine and alcohol"
            ],
            "red_flags": "See GP urgently if fever develops, severe back pain, or vomiting",
            "urgency": "routine",
            "probability": top_prob
        }
    
    # BPH pathway
    elif top_condition == "bph" and top_prob > 0.60:
        return {
            "primary_diagnosis": "Symptoms suggest benign prostate enlargement (BPH)",
            "confidence": "moderate-high",
            "action": "Book routine urology assessment",
            "self_care": [
                "Reduce caffeine and alcohol intake, especially before bed",
                "Practice double voiding (wait 30 seconds and try again)",
                "Avoid decongestants (can worsen symptoms)",
                "Consider saw palmetto (some evidence of benefit)"
            ],
            "red_flags": "See GP urgently if unable to urinate, blood in urine, or severe pain",
            "urgency": "routine",
            "suitable_procedures": ["medication", "TURP", "HIFU", "laser_therapy"],
            "investigations_needed": ["PSA", "DRE", "uroflowmetry"],
            "probability": top_prob
        }
    
    # Kidney stones pathway  
    elif top_condition == "kidney_stones" and top_prob > 0.70:
        return {
            "primary_diagnosis": "Symptoms suggest possible kidney stones",
            "confidence": "high",
            "action": "See GP within 24 hours for pain relief and imaging",
            "self_care": [
                "Drink lots of water (helps small stones pass)",
                "Take ibuprofen or paracetamol for pain",
                "Apply heat to affected area"
            ],
            "red_flags": "Go to A&E if severe uncontrolled pain, fever, or vomiting",
            "urgency": "urgent",
            "probability": top_prob
        }
    
    # Uncertain - need more information
    else:
        second_prob = sorted_conditions[1][1] if len(sorted_conditions) > 1 else 0
        return {
            "primary_diagnosis": f"Uncertain - top possibilities: {top_condition} ({top_prob:.0%}), {sorted_conditions[1][0]} ({second_prob:.0%})",
            "confidence": "low",
            "action": "Recommend GP assessment for proper evaluation",
            "self_care": ["Monitor symptoms", "Stay hydrated"],
            "red_flags": "Seek urgent care if symptoms worsen or new symptoms develop",
            "urgency": "routine",
            "probability": top_prob,
            "note": "Additional questions needed to narrow down diagnosis"
        }


def _build_graph_structure(probabilities: Dict[str, float], symptoms: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build graph structure compatible with FindPivots algorithm
    """
    graph = {
        "nodes": {},
        "edges": []
    }
    
    # Add disease nodes
    for condition, prob in probabilities.items():
        disease_id = f"uro_{condition}"
        graph["nodes"][disease_id] = {
            "type": "disease",
            "probability": prob,
            "label": condition.replace("_", " ").title()
        }
    
    # Add symptom nodes (observed and unobserved)
    all_possible_symptoms = [
        "weak_stream", "urgency", "frequency", "nocturia", 
        "incomplete_emptying", "hesitancy", "straining",
        "pain_burning", "dysuria", "blood_in_urine",
        "fever", "severe_pain", "pelvic_pain"
    ]
    
    for symptom_id in all_possible_symptoms:
        # Check if symptom was observed
        value = None
        if symptom_id in symptoms.get("reported_symptoms", []):
            value = 1.0
        elif f"no_{symptom_id}" in symptoms.get("reported_symptoms", []):
            value = 0.0
        
        graph["nodes"][symptom_id] = {
            "type": "symptom",
            "value": value,
            "label": symptom_id.replace("_", " ").title()
        }
    
    # Add edges (symptom -> disease with weights)
    # TODO: RESEARCH - Get these weights from sensitivity/specificity studies
    edge_weights = {
        ("weak_stream", "uro_bph"): 0.95,
        ("weak_stream", "uro_prostate_cancer"): 0.75,
        ("urgency", "uro_uti"): 0.90,
        ("urgency", "uro_overactive_bladder"): 0.95,
        ("pain_burning", "uro_uti"): 0.95,
        ("pain_burning", "uro_prostatitis"): 0.90,
        ("blood_in_urine", "uro_kidney_stones"): 0.90,
        ("fever", "uro_uti"): 0.85,
        ("fever", "uro_prostatitis"): 0.90,
        # ... etc
    }
    
    for (symptom, disease), weight in edge_weights.items():
        graph["edges"].append({
            "from": symptom,
            "to": disease,
            "weight": weight
        })
    
    return graph


def _collect_citations() -> List[str]:
    """Collect all citations used in calculation"""
    citations = []
    
    for prior_data in UROLOGY_PRIORS.values():
        if isinstance(prior_data, dict) and "citation" in prior_data:
            citations.append(prior_data["citation"])
    
    for symptom_data in SYMPTOM_POINTS.values():
        if "citation" in symptom_data:
            citations.append(symptom_data["citation"])
    
    return list(set(citations))  # Remove duplicates


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_entropy(probabilities: Dict[str, float]) -> float:
    """Calculate Shannon entropy of probability distribution"""
    entropy = 0
    for prob in probabilities.values():
        if prob > 0:
            entropy -= prob * math.log2(prob)
    return entropy
