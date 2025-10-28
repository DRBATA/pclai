"""
Procedural Calculators for Treatment Agent
Evidence-based scoring for biopsy, HIFU, and treatment pathways
Based on clinical_graph YAML specs and surgical intake form
"""

import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class CriterionMatch:
    """Represents a matched criterion with evidence"""
    label: str
    score_contribution: float
    evidence: str
    feature_value: Any
    threshold: float


def calculate_mri_fusion_indication(
    pirads: int,
    psad: float,
    psa_velocity: Optional[float] = None,
    lesion_size_mm: Optional[float] = None,
    fusion_available: bool = True
) -> Dict[str, Any]:
    """
    MRI Fusion Biopsy Indication Calculator
    Based on EAU 2025, NICE NG131, Carter JAMA 2021
    
    Returns scoring with evidence citations
    """
    
    # Evidence-tagged criteria from biopsy.yaml
    criteria = [
        {
            "feature": "PIRADS",
            "threshold": 4,
            "lr": 3.2,
            "weight": 1.3,
            "evidence": "EAU-2025-PI-RADS",
            "value": pirads
        },
        {
            "feature": "PSAD",
            "threshold": 0.15,
            "lr": 2.5,
            "weight": 1.0,
            "evidence": "NICE-NG131-2024",
            "value": psad
        },
        {
            "feature": "PSAV",
            "threshold": 1.5,
            "lr": 1.8,
            "weight": 0.6,
            "evidence": "Carter-JAMA-2021",
            "value": psa_velocity
        },
        {
            "feature": "LESION",
            "threshold": 8,
            "lr": 1.7,
            "weight": 0.5,
            "evidence": "Radiology-2020-Mehralivand",
            "value": lesion_size_mm
        }
    ]
    
    # Calculate score
    base_score = 1.0
    matched_criteria = []
    
    for crit in criteria:
        value = crit["value"]
        if value is not None and value >= crit["threshold"]:
            # Log-odds contribution: weight + log10(LR)
            contribution = crit["weight"] + math.log10(crit["lr"])
            base_score += contribution
            
            matched_criteria.append(CriterionMatch(
                label=f"{crit['feature']} ≥ {crit['threshold']}",
                score_contribution=round(contribution, 2),
                evidence=crit["evidence"],
                feature_value=value,
                threshold=crit["threshold"]
            ))
    
    # Thresholds from spec
    thresholds = {"score_low": 0.5, "score_high": 1.5}
    
    # Band classification
    if base_score >= thresholds["score_high"]:
        band = "strong"
        recommendation = "MRI fusion biopsy strongly indicated"
    elif base_score >= thresholds["score_low"]:
        band = "consider"
        recommendation = "Consider MRI fusion biopsy - discuss with patient"
    else:
        band = "weak"
        recommendation = "MRI fusion biopsy not strongly indicated on current criteria"
    
    # Site availability check
    site_block = None if fusion_available else "MR/US fusion software not available at this site"
    
    return {
        "calculator_name": "MRI_FUSION_INDICATIONS",
        "raw_score": round(base_score, 3),
        "band": band,
        "recommendation": recommendation,
        "matched_criteria": [
            {
                "label": m.label,
                "contribution": m.score_contribution,
                "evidence": m.evidence,
                "value": m.feature_value
            }
            for m in matched_criteria
        ],
        "thresholds": thresholds,
        "site_block": site_block,
        "consent_template": "Consent_Biopsy@v1.1" if band in ["strong", "consider"] else None,
        "urgency": "routine" if band == "strong" else "non_urgent"
    }


def calculate_hifu_eligibility(
    pirads: int,
    lesion_size_mm: float,
    gleason_score: str,
    prostate_volume_cc: float,
    hifu_available: bool = False
) -> Dict[str, Any]:
    """
    HIFU Focal Therapy Eligibility Calculator
    Based on EAU 2023, Ahmed 2021 Lancet Oncology
    
    Returns scoring with evidence citations and contraindications
    """
    
    # Evidence-tagged criteria from hifu.yaml
    criteria = [
        {
            "feature": "PIRADS",
            "threshold": 4,
            "lr": 1.6,
            "weight": 0.6,
            "evidence": "EAU-2023",
            "value": pirads
        },
        {
            "feature": "LESION",
            "threshold": 8,
            "lr": 1.9,
            "weight": 0.8,
            "evidence": "Ahmed-2021-LancetOnc",
            "value": lesion_size_mm
        },
        {
            "feature": "GLEASON_MAX",
            "threshold": 7,
            "lr": 2.1,
            "weight": 0.9,
            "evidence": "EAU-2023",
            "value": _gleason_to_numeric(gleason_score)
        }
    ]
    
    # Calculate base score
    base_score = 1.0
    matched_criteria = []
    
    for crit in criteria:
        value = crit["value"]
        if value is not None:
            # Special handling for Gleason (≤7 means suitable)
            if crit["feature"] == "GLEASON_MAX":
                meets_threshold = value <= crit["threshold"]
            else:
                meets_threshold = value >= crit["threshold"]
            
            if meets_threshold:
                contribution = crit["weight"] + math.log10(crit["lr"])
                base_score += contribution
                
                matched_criteria.append({
                    "label": f"{crit['feature']} suitable" if crit["feature"] == "GLEASON_MAX" else f"{crit['feature']} ≥ {crit['threshold']}",
                    "contribution": round(contribution, 2),
                    "evidence": crit["evidence"],
                    "value": value
                })
    
    # Contraindication: Large prostate
    contraindication_hit = prostate_volume_cc > 60
    if contraindication_hit:
        base_score -= 0.8  # Penalty from spec
    
    # Thresholds
    thresholds = {"score_low": 0.4, "score_high": 1.3}
    
    # Band classification
    if base_score >= thresholds["score_high"]:
        band = "strong"
        recommendation = "HIFU focal therapy may be suitable - refer to specialist"
    elif base_score >= thresholds["score_low"]:
        band = "consider"
        recommendation = "HIFU focal therapy could be discussed as an option"
    else:
        band = "weak"
        recommendation = "HIFU focal therapy not strongly indicated"
    
    # Site availability
    site_block = None if hifu_available else "HIFU not available at this site - would require referral"
    
    # Lesion size window (ideal 8-15mm)
    window_note = None
    if lesion_size_mm:
        if 8 <= lesion_size_mm <= 15:
            window_note = "Lesion size in ideal focal window (8–15 mm)"
        elif lesion_size_mm > 15:
            window_note = "Lesion >15 mm — focal margins may be challenging, may need hemi-ablation"
        else:
            window_note = "Lesion <8 mm — lower HIFU yield, consider monitoring"
    
    return {
        "calculator_name": "HIFU_ELIGIBILITY",
        "raw_score": round(base_score, 3),
        "band": band,
        "recommendation": recommendation,
        "matched_criteria": matched_criteria,
        "thresholds": thresholds,
        "site_block": site_block,
        "contraindications": {
            "large_prostate_gt60cc": contraindication_hit
        },
        "window_note": window_note,
        "consent_template": "Consent_HIFU@v1.3" if band in ["strong", "consider"] else None,
        "urgency": "elective",
        "estimated_cost_gbp": 16000 if not hifu_available else None  # Private cost if referral needed
    }


def calculate_active_surveillance_vs_surgery(
    age: int,
    psad: float,
    pirads: int,
    gleason_score: str,
    comorbidity: str,
    patient_preferences: Dict[str, float]
) -> Dict[str, Any]:
    """
    Non-prescriptive AS vs Surgery utility comparison
    
    Args:
        patient_preferences: Dict with keys:
            - urinary: 0-1 (concern about urinary function)
            - sexual: 0-1 (concern about sexual function)
            - avoid_overtreatment: 0-1 (preference to avoid unnecessary treatment)
    """
    
    # Active Surveillance score
    base_as = 0.6
    
    # Progression risk based on features
    progression_lr = 1.0
    if psad >= 0.15:
        progression_lr *= 2.0  # NICE flag
    if pirads >= 5:
        progression_lr *= 1.5
    if gleason_score in ["4+3", ">=8", "8", "9", "10"]:
        progression_lr *= 2.0
    if gleason_score == "3+3":
        progression_lr *= 0.7  # Lower risk
    
    as_harm = 0.15 * (progression_lr - 1)
    as_preference = 0.25 * patient_preferences.get("avoid_overtreatment", 0.5)
    as_score = base_as + as_preference - as_harm
    
    # Surgery (Radical Prostatectomy) score
    base_rp = 0.4
    
    # Cancer control benefit
    rp_benefit = 0.25
    if gleason_score in ["4+3", ">=8"]:
        rp_benefit += 0.15
    if pirads >= 5:
        rp_benefit += 0.1
    
    # Surgical harm/side effects
    comorbidity_harm = {"low": 0, "moderate": 0.08, "high": 0.15}.get(comorbidity, 0)
    pref_scale = 0.5 * (patient_preferences.get("urinary", 0.5) + patient_preferences.get("sexual", 0.5))
    
    rp_harm = 0.18 + comorbidity_harm + pref_scale
    if age >= 70:
        rp_harm += 0.07  # Age effect
    
    rp_score = base_rp + rp_benefit - rp_harm
    
    # Determine preference
    margin = abs(as_score - rp_score)
    if margin < 0.1:
        preference = "equipoise"
        note = "Scores very close - excellent candidate for shared decision making"
    elif as_score > rp_score:
        preference = "active_surveillance"
        note = "Active surveillance slightly favored based on risk/benefit profile"
    else:
        preference = "surgery"
        note = "Surgery slightly favored based on risk/benefit profile"
    
    return {
        "calculator_name": "AS_VS_SURGERY_UTILITY",
        "scores": {
            "active_surveillance": round(as_score, 3),
            "surgery_rp": round(rp_score, 3)
        },
        "preference": preference,
        "margin": round(margin, 3),
        "note": note,
        "factors": {
            "progression_lr": round(progression_lr, 2),
            "rp_benefit": round(rp_benefit, 2),
            "rp_harm": round(rp_harm, 2),
            "patient_preference_weight": round(pref_scale, 2)
        },
        "disclaimer": "For decision support only — not a medical directive. These are relative utilities, not probabilities."
    }


def _gleason_to_numeric(gleason: str) -> int:
    """Convert Gleason string to numeric for comparison"""
    if gleason == "3+3":
        return 6
    elif gleason == "3+4":
        return 7
    elif gleason == "4+3":
        return 7
    elif gleason in [">=8", "8", "9", "10"]:
        return int(gleason.replace(">=", ""))
    return 7  # Default


def generate_treatment_summary(
    patient_data: Dict[str, Any],
    mri_fusion_result: Dict[str, Any],
    hifu_result: Dict[str, Any],
    as_vs_surgery_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive treatment pathway summary
    Used by Treatment Agent for patient education and booking
    """
    
    # Determine primary pathway
    pathways = []
    
    if mri_fusion_result["band"] in ["strong", "consider"]:
        pathways.append({
            "name": "MRI Fusion Biopsy",
            "priority": "high" if mri_fusion_result["band"] == "strong" else "medium",
            "urgency": mri_fusion_result["urgency"],
            "evidence": [m["evidence"] for m in mri_fusion_result["matched_criteria"]],
            "next_steps": [
                "Book biopsy appointment",
                "Discuss anticoagulant management if applicable",
                "Provide patient information leaflet",
                "Arrange follow-up for results (2-3 weeks)"
            ],
            "site_constraint": mri_fusion_result.get("site_block")
        })
    
    if hifu_result["band"] in ["strong", "consider"] and not hifu_result["contraindications"]["large_prostate_gt60cc"]:
        pathways.append({
            "name": "HIFU Focal Therapy",
            "priority": "medium",
            "urgency": hifu_result["urgency"],
            "cost_estimate_gbp": hifu_result.get("estimated_cost_gbp"),
            "evidence": [m["evidence"] for m in hifu_result["matched_criteria"]],
            "next_steps": [
                "Specialist urology consultation required",
                "Discuss procedure risks and benefits",
                "Review MRI images with radiologist",
                "Cost discussion if private procedure"
            ],
            "site_constraint": hifu_result.get("site_block"),
            "window_note": hifu_result.get("window_note")
        })
    
    # AS vs Surgery recommendation
    if as_vs_surgery_result["preference"] == "active_surveillance":
        pathways.append({
            "name": "Active Surveillance",
            "priority": "medium",
            "urgency": "routine",
            "next_steps": [
                "Schedule 6-month PSA check",
                "Repeat MRI in 12 months",
                "Patient education on monitoring schedule",
                "Lifestyle modification discussion"
            ]
        })
    elif as_vs_surgery_result["preference"] == "surgery":
        pathways.append({
            "name": "Radical Prostatectomy (Surgery)",
            "priority": "medium",
            "urgency": "elective",
            "next_steps": [
                "Referral to urological surgeon",
                "Pre-operative assessment",
                "Discuss surgical approach (robotic vs open)",
                "Consent and side effect counselling"
            ]
        })
    
    # Booking recommendations
    booking_recommendation = {
        "suggested_timing": _determine_booking_timing(pathways),
        "theatre_priority": _determine_theatre_priority(pathways, patient_data),
        "patient_readiness": _assess_patient_readiness(patient_data, pathways)
    }
    
    return {
        "summary": {
            "pathways": pathways,
            "booking": booking_recommendation,
            "patient_data": patient_data,
            "confidence": "moderate" if pathways else "low"
        },
        "patient_email_content": _generate_patient_email(pathways, patient_data),
        "clinical_summary": _generate_clinical_summary(pathways, patient_data, mri_fusion_result, hifu_result)
    }


def _determine_booking_timing(pathways: List[Dict]) -> str:
    """Determine when to book based on pathway urgencies"""
    urgencies = [p["urgency"] for p in pathways]
    
    if "urgent" in urgencies:
        return "within_2_weeks"
    elif "routine" in urgencies:
        return "within_6_weeks"
    else:
        return "elective_3_6_months"


def _determine_theatre_priority(pathways: List[Dict], patient_data: Dict) -> str:
    """Help manage theatre capacity"""
    # Consider: Gleason score, age, PSA, patient preference
    gleason = patient_data.get("gleason_score", "")
    age = patient_data.get("age", 70)
    
    if gleason in ["4+3", ">=8"] or any(p["priority"] == "high" for p in pathways):
        return "priority"  # Book sooner
    elif age < 65:
        return "standard"
    else:
        return "flexible"  # Can accommodate schedule


def _assess_patient_readiness(patient_data: Dict, pathways: List[Dict]) -> Dict[str, Any]:
    """Assess if patient is ready to book or needs more discussion"""
    
    concerns = []
    
    # Check if patient has all information
    if not pathways:
        concerns.append("No clear pathway identified - more investigation needed")
    
    # Check for high anxiety about side effects
    prefs = patient_data.get("preferences", {})
    if prefs.get("urinary", 0) > 0.8 or prefs.get("sexual", 0) > 0.8:
        concerns.append("High concern about side effects - extended counselling recommended")
    
    # Check for site constraints
    if any(p.get("site_constraint") for p in pathways):
        concerns.append("Procedure not available at site - referral discussion needed")
    
    readiness = "ready_to_book" if not concerns else "needs_discussion"
    
    return {
        "readiness": readiness,
        "concerns": concerns,
        "recommended_next_step": "Book appointment" if readiness == "ready_to_book" else "Schedule consultation call"
    }


def _generate_patient_email(pathways: List[Dict], patient_data: Dict) -> str:
    """Generate patient-friendly email content"""
    
    content = f"""Dear Patient,

Thank you for discussing your prostate health with us. Based on our conversation, here's what we recommend:

"""
    
    for i, pathway in enumerate(pathways, 1):
        content += f"""
{i}. {pathway['name']}
   Why: Based on your PSA levels, MRI findings, and personal preferences
   Next steps: {', '.join(pathway['next_steps'][:2])}
   Timing: {pathway['urgency'].replace('_', ' ').title()}
"""
    
    content += """

What This Means For You:
- These recommendations are designed to give you options, not prescribe a single path
- We're here to discuss any concerns you have about procedures or side effects
- All treatments have risks and benefits - we'll explain these in detail

Next Steps:
- Review the attached information sheets
- Note any questions you have
- We'll contact you within 48 hours to schedule a follow-up

Questions? Reply to this email or call our clinic.

Best regards,
Your Urology Team
"""
    
    return content


def _generate_clinical_summary(
    pathways: List[Dict],
    patient_data: Dict,
    mri_result: Dict,
    hifu_result: Dict
) -> str:
    """Generate clinical summary for EMR (de-identified)"""
    
    return f"""CLINICAL DECISION SUPPORT SUMMARY

Assessment Date: [AUTO-GENERATED]

Patient Profile:
- Age: {patient_data.get('age', 'N/A')}
- PSA: {patient_data.get('psa', 'N/A')} ng/mL
- PSA Density: {patient_data.get('psad', 'N/A')}
- PI-RADS: {patient_data.get('pirads', 'N/A')}
- Gleason: {patient_data.get('gleason_score', 'N/A')}
- Comorbidity: {patient_data.get('comorbidity', 'N/A')}

MRI Fusion Biopsy Indication: {mri_result['band'].upper()}
- Score: {mri_result['raw_score']}
- Evidence: {', '.join([m['evidence'] for m in mri_result['matched_criteria']])}

HIFU Eligibility: {hifu_result['band'].upper()}
- Score: {hifu_result['raw_score']}
- Contraindications: {'Large prostate >60cc' if hifu_result['contraindications']['large_prostate_gt60cc'] else 'None identified'}

Recommended Pathways:
{chr(10).join([f"- {p['name']} ({p['priority']} priority)" for p in pathways])}

Decision Support Algorithm Version: 2.0
Evidence Base: EAU 2023-2025, NICE NG131-2024, Ahmed 2021

Note: This is decision support output. Clinical judgment and MDT review required.
"""
