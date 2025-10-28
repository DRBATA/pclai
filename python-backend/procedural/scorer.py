"""
Procedural Decision Scorer
Deterministic, explainable scoring for surgical/procedural pathways
Clinical graphs stored in YAML (versioned, auditable)
"""

import math
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple


CLINICAL_GRAPH_DIR = Path(__file__).parent.parent / "clinical_graph"


def load_calculator(calc_name: str) -> Dict[str, Any]:
    """
    Load a clinical calculator from YAML
    
    Args:
        calc_name: Name of calculator file (e.g., "biopsy", "hifu")
        
    Returns:
        Dict with calculator configuration
    """
    calc_path = CLINICAL_GRAPH_DIR / f"{calc_name}.yaml"
    with open(calc_path, "r") as f:
        return yaml.safe_load(f)


def feature_meets(feature_name: str, patient_value: Any, threshold: float) -> bool:
    """
    Check if patient's feature value meets threshold
    
    Default: ≥ threshold (can customize for specific features)
    
    Args:
        feature_name: Name of the feature
        patient_value: Patient's value for this feature
        threshold: Threshold to meet
        
    Returns:
        True if feature meets criteria
    """
    if patient_value is None:
        return False
    
    # Special cases for certain features
    if feature_name == "GLEASON_MAX":
        # For Gleason, threshold is maximum (≤ threshold)
        return float(patient_value) <= float(threshold)
    
    # Default: ≥ threshold
    return float(patient_value) >= float(threshold)


def score_calculator(calc_yaml: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score a calculator based on patient features
    
    Uses likelihood ratios and weights to calculate a soft score
    
    Args:
        calc_yaml: Calculator configuration
        features: Patient feature values
        
    Returns:
        Dict with score, evidence hits, and thresholds
    """
    # Multiply LRs for met supports; sum weights; add decision output_weight
    lr_prod = 1.0
    w_sum = 0.0
    hit = []
    
    for crit in calc_yaml.get("criteria", []):
        for s in crit.get("supports", []):
            if feature_meets(s["feature"], features.get(s["feature"]), s["threshold"]):
                lr_prod *= float(s["lr"])
                w_sum += float(s.get("weight", 0.0))
                hit.append({
                    "feature": s["feature"],
                    "threshold": s["threshold"],
                    "patient_value": features.get(s["feature"]),
                    "lr": s["lr"],
                    "weight": s.get("weight", 0.0),
                    "evidence": s["evidence"]
                })
    
    # Add output weight from decision
    decisions = calc_yaml.get("decisions", [])
    out_w = max(d.get("output_weight", 0.0) for d in decisions) if decisions else 0.0
    
    # Calculate soft score: log10(LR product) + weight sum + output weight
    soft_score = math.log10(lr_prod) + w_sum + out_w
    
    return {
        "score": round(soft_score, 3),
        "hits": hit,
        "thresholds": calc_yaml.get("thresholds", {}),
        "decision_name": decisions[0]["name"] if decisions else None,
        "consent_template": decisions[0].get("consent_template") if decisions else None
    }


def contraindicated(calc_yaml: Dict[str, Any], decision_name: str, features: Dict[str, Any]) -> Tuple[bool, Dict]:
    """
    Check if decision is contraindicated for this patient
    
    Args:
        calc_yaml: Calculator configuration
        decision_name: Name of decision to check
        features: Patient features
        
    Returns:
        Tuple of (is_contraindicated, contraindication_details)
    """
    for c in calc_yaml.get("contraindications", []):
        if c["decision"] == decision_name:
            v = features.get(c["feature"])
            if v is None:
                continue
            
            if c["op"] == ">" and float(v) > float(c["value"]):
                return True, c
            if c["op"] == "<" and float(v) < float(c["value"]):
                return True, c
            if c["op"] == "==" and float(v) == float(c["value"]):
                return True, c
    
    return False, {}


def route_role(scores: Dict[str, float], red_flags: List[str]) -> Tuple[str, bool, float]:
    """
    Route to appropriate clinical role based on complexity and red flags
    
    Args:
        scores: Dict of calculator scores
        red_flags: List of red flag conditions
        
    Returns:
        Tuple of (assigned_role, signoff_required, complexity_score)
    """
    # Complexity = max score
    complexity = max(scores.values()) if scores else 0.0
    
    # Red flags always go to doctor
    if red_flags:
        return "Urologist_Doctor", True, complexity
    
    # Route based on complexity
    if complexity <= 0.5:
        return "Prostate_Specialist_Nurse", False, complexity
    
    if complexity < 1.2:
        # PA can prep; MD signs off
        return "Physician_Associate", True, complexity
    
    return "Urologist_Doctor", True, complexity


def decide_and_prepare(patient_features: Dict[str, Any], red_flags: List[str] = None) -> Dict[str, Any]:
    """
    Main decision function: Score patient for procedures and prepare routing
    
    Args:
        patient_features: Dict of patient features (PIRADS, PSAD, etc.)
        red_flags: List of red flag conditions (default: [])
        
    Returns:
        Dict with procedural plan, routing, and next steps
    """
    if red_flags is None:
        red_flags = []
    
    # Load calculators
    biopsy = load_calculator("biopsy")
    hifu = load_calculator("hifu")
    
    # Score each calculator
    s_b = score_calculator(biopsy, patient_features)
    s_h = score_calculator(hifu, patient_features)
    
    scores = {
        "MRI_FUSION_INDICATIONS": s_b["score"],
        "HIFU_ELIGIBILITY": s_h["score"]
    }
    
    # Route to appropriate role
    role, needs_signoff, complexity = route_role(scores, red_flags)
    
    # Check HIFU contraindications
    hifu_block, block_meta = contraindicated(hifu, "Discuss_Focal_HIFU", patient_features)
    
    # Build plan
    plan = {
        "assigned_role": role,
        "signoff_required": needs_signoff,
        "complexity": round(complexity, 3),
        "biopsy": {
            "score": s_b["score"],
            "interpretation": (
                "discuss MRI-fusion biopsy" if s_b["score"] >= s_b["thresholds"].get("score_high", 1.5)
                else "consider imaging discussion" if s_b["score"] >= s_b["thresholds"].get("score_low", 0.5)
                else "consider surveillance / repeat interval"
            ),
            "evidence_hits": s_b["hits"],
            "consent_template": s_b.get("consent_template")
        },
        "hifu": {
            "score": s_h["score"],
            "contraindicated": bool(hifu_block),
            "contra_reason": block_meta if hifu_block else None,
            "interpretation": (
                "discuss focal HIFU (after MD sign-off & consent)"
                if (s_h["score"] >= s_h["thresholds"].get("score_high", 1.3) and not hifu_block)
                else "not a focal candidate / consider alternatives"
            ),
            "evidence_hits": s_h["hits"],
            "consent_template": s_h.get("consent_template") if not hifu_block else None
        },
        "next_steps": _get_next_steps(role),
        "red_flags": red_flags
    }
    
    return plan


def _get_next_steps(role: str) -> List[str]:
    """Get next steps based on assigned role"""
    if role == "Prostate_Specialist_Nurse":
        return [
            "Run Intake/Safety assessment",
            "Present consent options to patient",
            "Prepare booking packet",
            "Schedule follow-up"
        ]
    elif role == "Physician_Associate":
        return [
            "Run Intake/Education session",
            "Collate investigation results and documentation",
            "Await MD sign-off before any pathway decision",
            "Prepare consent discussions"
        ]
    else:  # Urologist_Doctor
        return [
            "Review calculator outputs and evidence",
            "Conduct consent discussion with patient",
            "Confirm procedural pathway and sign off",
            "Schedule procedure or surveillance plan"
        ]


def format_procedural_summary(plan: Dict[str, Any]) -> str:
    """
    Format the procedural plan as human-readable text
    
    Args:
        plan: Output from decide_and_prepare
        
    Returns:
        Formatted summary string
    """
    summary = f"""
## Procedural Decision Summary

**Assigned Role:** {plan['assigned_role']}
**Signoff Required:** {'Yes' if plan['signoff_required'] else 'No'}
**Case Complexity Score:** {plan['complexity']}

### MRI-Fusion Biopsy Indication
**Score:** {plan['biopsy']['score']}
**Recommendation:** {plan['biopsy']['interpretation']}

**Evidence Supporting This Decision:**
"""
    
    for hit in plan['biopsy']['evidence_hits']:
        summary += f"- {hit['feature']}: {hit['patient_value']} (threshold: {hit['threshold']}, LR: {hit['lr']}, evidence: {hit['evidence']})\n"
    
    summary += f"\n### Focal HIFU Eligibility\n"
    summary += f"**Score:** {plan['hifu']['score']}\n"
    summary += f"**Recommendation:** {plan['hifu']['interpretation']}\n"
    
    if plan['hifu']['contraindicated']:
        contra = plan['hifu']['contra_reason']
        summary += f"\n⚠️ **Contraindication:** {contra['feature']} {contra['op']} {contra['value']} (evidence: {contra['evidence']})\n"
    else:
        summary += f"\n**Evidence Supporting This Decision:**\n"
        for hit in plan['hifu']['evidence_hits']:
            summary += f"- {hit['feature']}: {hit['patient_value']} (threshold: {hit['threshold']}, LR: {hit['lr']}, evidence: {hit['evidence']})\n"
    
    summary += f"\n### Next Steps\n"
    for i, step in enumerate(plan['next_steps'], 1):
        summary += f"{i}. {step}\n"
    
    if plan['red_flags']:
        summary += f"\n⚠️ **Red Flags Present:** {', '.join(plan['red_flags'])}\n"
    
    return summary
