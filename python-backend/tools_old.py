import json
from agents import function_tool, RunContextWrapper
from py_mini_racer import MiniRacer
from typing import Dict, Any, List

# Path to the JavaScript file with clinical calculations.
# This will be used by our Calculator tool.
JS_CALCULATIONS_FILE = "c:/Users/azamb/OneDrive/Documents/EasyGP.COM/multiagent/differentialCalculations.jsx"

def get_js_code():
    """
    Reads the JavaScript code from the file and removes 'export' statements
    so it can be executed by the MiniRacer context.
    """
    with open(JS_CALCULATIONS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        js_code = f.read()
    # Remove 'export' so the functions are defined in the global scope of the JS context
    return js_code.replace("export function", "function")

# Create a single, reusable JS context to avoid re-initializing and re-parsing the code on every call.
# This is much more efficient.
ctx = MiniRacer()
js_code = get_js_code()
ctx.eval(js_code)

@function_tool(
    name_override="calculator_tool",
    description_override="Run a clinical calculation from differentialCalculations.js"
)
def run_symptom_calculation(function_name: str, value: int) -> float:
    """
    A 'Calculator' tool for the Private Investigator (PI) agent.
    It runs a specific clinical calculation from the 'differentialCalculations.jsx' file.

    :param function_name: The exact name of the JavaScript function to call (e.g., 'calculateTonsilStrepLikelihood').
    :param value: The integer value of the symptom being measured (e.g., a swelling score of 85).
    :return: The calculated probability as a float.
    """
    try:
        # Call the specific function within the JS context
        result = ctx.call(function_name, value)
        return float(result)
    except Exception as e:
        print(f"Error calling JS function '{function_name}' with value '{value}': {e}")
        # In case of an error (e.g., function not found), return a neutral probability to avoid breaking the agent flow.
        return 0.0


@function_tool(
    name_override="check_safety_concerns",
    description_override="Check for red flag symptoms and emergency conditions using keyword matching"
)
def check_safety_concerns(symptoms_description: str, age: int | None = None) -> Dict[str, Any]:
    """
    Check for red flag symptoms and safety concerns based on reported symptoms.
    Uses fast local keyword matching against clinical red flags database.
    
    :param symptoms_description: Comprehensive description of all symptoms mentioned by the user
    :param age: Patient's age (optional, important for pediatric checks)
    :return: Dictionary with safety check results including red flags, severity, and recommended actions
    """
    try:
        from safety.local_checker import local_checker
        
        # Run local red flag check
        result = local_checker.check(symptoms_description, age=age)
        
        # Format response for agent
        response = {
            "has_red_flags": result["has_red_flags"],
            "highest_severity": result["highest_severity"],
            "urgent_escalation_needed": result["urgent_escalation_needed"],
            "recommended_action": result["recommended_action"],
            "concerns_found": result["concerns_found"],
            "concerns": [
                {
                    "title": c["title"],
                    "category": c["category"],
                    "severity": c["severity"],
                    "action": c["action"],
                    "timeframe": c["timeframe"],
                    "matched_trigger": c["matched_trigger"],
                    "key_negatives": c.get("key_negatives", [])
                }
                for c in result["concerns"][:3]  # Top 3 concerns only
            ]
        }
        
        return response
        
    except Exception as e:
        print(f"Error checking safety concerns: {e}")
        import traceback
        traceback.print_exc()
        return {
            "has_red_flags": False,
            "error": str(e),
            "note": "Safety check unavailable - proceeding with caution"
        }


@function_tool(
    name_override="calculate_pain_conditions",
    description_override="Calculate probabilities for musculoskeletal pain conditions based on symptoms"
)
def calculate_pain_conditions(symptom_scores: str) -> Dict[str, Any]:
    """
    Calculate differential probabilities for pain/musculoskeletal conditions.
    
    :param symptom_scores: JSON string of symptom scores, e.g. '{"joint_pain": 8, "swelling": 6, "stiffness": 7}'
                           Scores should be 0-10 where 10 is maximum intensity
    :return: Dictionary with ranked condition probabilities
    """
    try:
        from differentials.pain_conditions import PAIN_SYMPTOM_MATRIX, calculate_condition_probability
        
        # Parse symptom scores
        scores = json.loads(symptom_scores) if isinstance(symptom_scores, str) else symptom_scores
        
        # Calculate probability for each condition
        results = []
        for condition_id, condition_data in PAIN_SYMPTOM_MATRIX.items():
            prob = calculate_condition_probability(condition_id, scores)
            if prob > 0.1:  # Only include if >10% probability
                results.append({
                    "condition": condition_data["name"],
                    "condition_id": condition_id,
                    "probability": round(prob, 3),
                    "percentage": round(prob * 100, 1),
                    "pattern": condition_data["typical_pattern"]
                })
        
        # Sort by probability
        results.sort(key=lambda x: x["probability"], reverse=True)
        
        return {
            "top_condition": results[0] if results else None,
            "differentials": results[:5],  # Top 5
            "total_conditions_considered": len(PAIN_SYMPTOM_MATRIX),
            "note": "Probabilities based on symptom pattern matching. Clinical correlation required."
        }
        
    except Exception as e:
        print(f"Error calculating pain conditions: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "Pain calculation unavailable"
        }


@function_tool(
    name_override="check_pharmacy_pathway",
    description_override="Check if patient is eligible for UK Pharmacy First pathway (pharmacist can prescribe antibiotics)"
)
def check_pharmacy_pathway(
    condition: str,
    age: int,
    gender: str,
    symptoms: str,
    red_flags: str = "",
    contraindications: str = "",
    duration_days: int | None = None,
    pregnant: bool = False
) -> Dict[str, Any]:
    """
    Check eligibility for UK Pharmacy First pathways.
    
    :param condition: Suspected condition (uti, shingles, impetigo, insect_bite, sore_throat, sinusitis, otitis_media)
    :param age: Patient age in years
    :param gender: Patient gender (Male, Female, Other)
    :param symptoms: Comma-separated symptoms (e.g. "painful_urination,frequent_urination")
    :param red_flags: Comma-separated red flags if any
    :param contraindications: Comma-separated medical conditions/contraindications
    :param duration_days: How many days symptoms have been present
    :param pregnant: Is patient pregnant
    :return: Dictionary with eligibility result and recommendations
    """
    try:
        from differentials.pharmacy_pathways import check_pharmacy_eligibility
        
        # Parse comma-separated inputs
        symptom_list = [s.strip() for s in symptoms.split(",") if s.strip()]
        red_flag_list = [s.strip() for s in red_flags.split(",") if s.strip()] if red_flags else []
        contraindication_list = [s.strip() for s in contraindications.split(",") if s.strip()] if contraindications else []
        
        # Check eligibility
        result = check_pharmacy_eligibility(
            condition=condition,
            age=age,
            gender=gender,
            symptoms=symptom_list,
            red_flags=red_flag_list,
            contraindications=contraindication_list,
            duration_days=duration_days,
            pregnant=pregnant
        )
        
        return {
            "eligible": result.eligible,
            "condition": result.condition,
            "reason": result.reason,
            "recommended_action": result.recommended_action,
            "medications": result.medications,
            "warnings": result.contraindication_warnings,
            "red_flags_present": result.red_flags
        }
        
    except Exception as e:
        print(f"Error checking pharmacy pathway: {e}")
        import traceback
        traceback.print_exc()
        return {
            "eligible": False,
            "error": str(e),
            "note": "Pharmacy pathway check unavailable - recommend GP consultation"
        }


@function_tool(
    name_override="get_clinical_guidance",
    description_override="Get clinical context and interpretation guidance for symptoms"
)
def get_clinical_guidance(symptoms: str) -> Dict[str, Any]:
    """
    Get clinical pearls, interpretation guidance, and key questions for reported symptoms.
    
    :param symptoms: Comma-separated symptoms (e.g. "sore throat, cough, fever")
    :return: Dictionary with clinical context and guidance
    """
    try:
        from differentials.clinical_context import get_interpretation_guidance, ESSENTIAL_QUESTIONS, CLINICAL_PEARLS
        
        # Parse symptoms
        symptom_list = [s.strip().lower() for s in symptoms.split(",") if s.strip()]
        
        # Get interpretation guidance
        guidance = get_interpretation_guidance(symptom_list)
        
        # Extract relevant pearls
        relevant_pearls = []
        if any("throat" in s for s in symptom_list):
            relevant_pearls.append(CLINICAL_PEARLS.get("swollen_glands"))
            relevant_pearls.append(CLINICAL_PEARLS.get("tonsillitis"))
        
        # Get essential questions
        key_questions = [
            ESSENTIAL_QUESTIONS["bacterial_vs_viral"]["question"],
            ESSENTIAL_QUESTIONS["upper_vs_lower_respiratory"]["question"],
            ESSENTIAL_QUESTIONS["seasonal_triggers"]["question"]
        ]
        
        return {
            "interpretation_guidance": guidance,
            "key_differentiating_questions": key_questions,
            "clinical_pearls": [p for p in relevant_pearls if p],
            "note": "Use this context to inform your analysis and recommendations"
        }
        
    except Exception as e:
        print(f"Error getting clinical guidance: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "Clinical guidance unavailable"
        }


@function_tool(
    name_override="get_next_safety_question",
    description_override="Get the next mandatory safety question that hasn't been asked yet"
)
def get_next_safety_question(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Returns the next mandatory safety question that must be asked.
    These questions MUST be asked before entropy-driven strategic questions.
    
    :return: Next safety question or indication that all safety questions are complete
    """
    try:
        from differentials.graph_builder import MANDATORY_SAFETY_QUESTIONS
        
        # Get list of already asked safety questions
        asked = context.context.safety_questions_asked if hasattr(context.context, 'safety_questions_asked') else []
        
        # Find first question that hasn't been asked
        for sq in MANDATORY_SAFETY_QUESTIONS:
            if sq["id"] not in asked:
                return {
                    "safety_question_id": sq["id"],
                    "question": sq["question"],
                    "rationale": sq["rationale"],
                    "rules_out": sq["rules_out"],
                    "safety_phase_complete": False,
                    "total_safety_questions": len(MANDATORY_SAFETY_QUESTIONS),
                    "questions_remaining": len(MANDATORY_SAFETY_QUESTIONS) - len(asked)
                }
        
        # All safety questions have been asked
        return {
            "safety_phase_complete": True,
            "message": "All mandatory safety questions have been asked. You may now proceed with entropy-driven strategic questions.",
            "total_safety_questions_asked": len(MANDATORY_SAFETY_QUESTIONS)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "note": "Failed to get safety question"
        }


@function_tool(
    name_override="record_safety_question_asked",
    description_override="Mark a mandatory safety question as asked"
)
def record_safety_question_asked(
    context: RunContextWrapper[Any],
    safety_question_id: str
) -> Dict[str, Any]:
    """
    Record that a mandatory safety question has been asked.
    
    :param safety_question_id: ID of the safety question that was asked
    :return: Confirmation message
    """
    try:
        if not hasattr(context.context, 'safety_questions_asked'):
            context.context.safety_questions_asked = []
        
        if safety_question_id not in context.context.safety_questions_asked:
            context.context.safety_questions_asked.append(safety_question_id)
        
        from differentials.graph_builder import MANDATORY_SAFETY_QUESTIONS
        total = len(MANDATORY_SAFETY_QUESTIONS)
        asked = len(context.context.safety_questions_asked)
        
        return {
            "success": True,
            "message": f"Recorded safety question: {safety_question_id}",
            "safety_questions_completed": asked,
            "safety_questions_total": total,
            "safety_phase_complete": asked >= total
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "note": "Failed to record safety question"
        }


@function_tool(
    name_override="build_probability_graph",
    description_override="Build probability graph using Bayesian calculator with evidence-based priors"
)
def build_probability_graph(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Build probability graph using the real Bayesian calculator (urology_calculator.py)
    This replaces the fake symptom matrix approach with evidence-based calculations
    
    :return: Dictionary with probabilities, graph structure, and clinical recommendations
    """
    try:
        from differentials.urology_calculator import compute_urology_differential, calculate_entropy
        from differentials.graph_engine import ProbabilityGraph
        
        print(f"DEBUG build_probability_graph: Starting with reported_symptoms = {context.context.reported_symptoms}")
        
        # Prepare symptoms dict for calculator
        symptoms = {
            "reported_symptoms": context.context.reported_symptoms,
            "onset_speed": context.context.__dict__.get("onset_speed"),
            "dysuria_severity": context.context.__dict__.get("dysuria_severity", 0),
            "weak_stream_severity": context.context.__dict__.get("weak_stream_severity", 0),
            "pain_severity": context.context.__dict__.get("pain_severity", 0),
            "fever_present": context.context.__dict__.get("fever_present", False),
            "nocturia_per_night": context.context.__dict__.get("nocturia_per_night", 0)
        }
        
        # Prepare patient info
        patient_info = {
            "age": context.context.age or 50,
            "gender": context.context.gender,
            "family_history_prostate_cancer": context.context.__dict__.get("family_history_prostate_cancer", False),
            "previous_kidney_stones": context.context.__dict__.get("previous_kidney_stones", False)
        }
        
        print(f"DEBUG build_probability_graph: Calling calculator with symptoms={symptoms}, patient_info={patient_info}")
        
        # Call the REAL Bayesian calculator
        result = compute_urology_differential(symptoms, patient_info)
        
        print(f"DEBUG build_probability_graph: Calculator returned probabilities = {result['probabilities']}")
        
        # Store graph in context (for FindPivots to use)
        context.context.probability_graph = result["graph"]
        
        # Calculate entropy
        entropy = calculate_entropy(result["probabilities"])
        context.context.current_entropy = entropy
        
        # Format top differentials
        sorted_probs = sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True)
        top_differentials = [
            {
                "condition": cond.replace("_", " ").title(),
                "condition_id": f"uro_{cond}",
                "probability": prob,
                "percentage": round(prob * 100, 1)
            }
            for cond, prob in sorted_probs[:3]
        ]
        
        # Store in context
        context.context.calculated_differentials = {
            f"uro_{cond}": prob for cond, prob in result["probabilities"].items()
        }
        
        graph = result["graph"]
        
        return {
            "graph_built": True,
            "total_nodes": len(graph["nodes"]),
            "total_edges": len(graph["edges"]),
            "symptom_nodes": len([n for n in graph["nodes"].values() if n["type"] == "symptom"]),
            "disease_nodes": len([n for n in graph["nodes"].values() if n["type"] == "disease"]),
            "initial_entropy": round(entropy, 3),
            "top_differentials": top_differentials,
            "recommendation": result["recommendation"],
            "data_sources": result["citations"],
            "note": "Graph built using evidence-based Bayesian calculator"
        }
        
    except Exception as e:
        print(f"Error building probability graph: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "Graph building failed"
        }


@function_tool(
    name_override="find_strategic_questions",
    description_override="Use FindPivots algorithm to identify most informative questions based on current probabilities"
)
def find_strategic_questions(context: RunContextWrapper[Any], max_questions: int = 3) -> Dict[str, Any]:
    """
    Apply FindPivots algorithm to find most strategic symptoms to ask about.
    Works with graph structure from the Bayesian calculator.
    
    :param max_questions: Maximum number of questions to suggest
    :return: Dictionary with suggested questions ranked by information gain
    """
    try:
        from differentials.graph_engine import ProbabilityGraph, find_pivots, choose_next_question, expected_information_gain
        from differentials.graph_builder import format_siqorstaa_question
        
        # Get graph from context (built by calculator)
        graph_dict = context.context.probability_graph
        if not graph_dict:
            return {"error": "No graph in context. Call build_probability_graph first."}
        
        print(f"DEBUG find_strategic_questions: Graph has {len(graph_dict.get('nodes', {}))} nodes")
        
        # Convert to ProbabilityGraph object
        graph = ProbabilityGraph()
        graph.nodes = graph_dict["nodes"]
        graph.edges = graph_dict["edges"]
        
        # Get known symptoms as seed
        known_symptoms = [
            node_id for node_id, node in graph.nodes.items()
            if node["type"] == "symptom" and node.get("value") is not None
        ]
        
        print(f"DEBUG find_strategic_questions: Known symptoms (seeds) = {known_symptoms}")
        
        if not known_symptoms:
            # No symptoms yet - suggest based on current probabilities
            print("DEBUG find_strategic_questions: No seeds yet, returning high-value initial questions")
            return {
                "pivot_count": 0,
                "working_set_size": 0,
                "suggested_questions": [
                    {
                        "symptom_id": "onset_speed",
                        "question": "Did your symptoms start suddenly (hours/days) or gradually over weeks/months?",
                        "information_gain": 0.8,
                        "type": "choice",
                        "reason": "Onset speed strongly differentiates acute (UTI/stones) from chronic (BPH/OAB) conditions"
                    },
                    {
                        "symptom_id": "pain_burning",
                        "question": "Do you have pain or burning when urinating?",
                        "information_gain": 0.7,
                        "type": "yes_no",
                        "reason": "Dysuria is highly specific for infection or inflammation"
                    }
                ],
                "note": "Initial high-value questions to establish diagnostic direction"
            }
        
        # Run FindPivots with known symptoms
        print(f"DEBUG find_strategic_questions: Running FindPivots with seeds={known_symptoms}")
        pivots, working_set = find_pivots(graph, known_symptoms, B=1.0, k=3)
        
        print(f"DEBUG find_strategic_questions: FindPivots returned pivots={pivots}, working_set={working_set}")
        
        # Store pivot nodes in context
        context.context.pivot_nodes = list(pivots)
        
        # Find best questions within working set
        questions = []
        checked = set(known_symptoms)  # Don't ask about known symptoms
        
        for _ in range(max_questions):
            next_symptom = choose_next_question(graph, working_set)
            if not next_symptom or next_symptom in checked:
                break
            
            checked.add(next_symptom)
            node = graph.nodes.get(next_symptom, {})
            gain = expected_information_gain(graph, next_symptom)
            
            print(f"DEBUG find_strategic_questions: Suggesting symptom={next_symptom}, gain={gain}")
            
            questions.append({
                "symptom_id": next_symptom,
                "question": format_siqorstaa_question(next_symptom, node.get("label", next_symptom)),
                "information_gain": round(gain, 3),
                "type": "scale_0_10" if any(word in next_symptom for word in ["pain", "severity", "swelling"]) else "yes_no"
            })
        
        return {
            "pivot_count": len(pivots),
            "working_set_size": len(working_set),
            "suggested_questions": questions,
            "note": "Ask these questions in order for maximum diagnostic clarity" if questions else "No additional strategic questions found"
        }
        
    except Exception as e:
        print(f"Error finding strategic questions: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "FindPivots failed"
        }


@function_tool(
    name_override="update_graph_with_answer",
    description_override="Update probability graph with patient's answer and propagate changes"
)
def update_graph_with_answer(
    context: RunContextWrapper[Any],
    symptom_id: str,
    value: float
) -> Dict[str, Any]:
    """
    Update graph with new symptom value and propagate probabilities.
    
    :param symptom_id: ID of symptom being answered
    :param value: Value (0-1 for yes/no, 0-10 for severity scales)
    :return: Updated graph state and new differential probabilities
    """
    try:
        from differentials.graph_engine import ProbabilityGraph, update_graph, propagate_update, get_total_entropy
        from differentials.graph_builder import extract_differential_results
        
        # Reconstruct graph
        graph_dict = context.context.probability_graph
        if not graph_dict:
            return {"error": "No graph in context"}
        
        graph = ProbabilityGraph()
        graph.nodes = graph_dict["nodes"]
        graph.edges = graph_dict["edges"]
        
        # Normalize value to 0-1 if it's a 0-10 scale
        if value > 1:
            normalized_value = value / 10.0
        else:
            normalized_value = value
        
        # Update and propagate
        graph = update_graph(graph, symptom_id, normalized_value)
        graph = propagate_update(graph, symptom_id)
        
        # Store updated graph
        context.context.probability_graph = graph.to_dict()
        
        # CRITICAL: Also update context.reported_symptoms so future graph builds have this symptom
        if normalized_value > 0 and symptom_id not in context.context.reported_symptoms:
            context.context.reported_symptoms.append(symptom_id)
            print(f"DEBUG update_graph_with_answer: Added '{symptom_id}' to reported_symptoms")
        elif normalized_value == 0 and symptom_id in context.context.reported_symptoms:
            context.context.reported_symptoms.remove(symptom_id)
            print(f"DEBUG update_graph_with_answer: Removed '{symptom_id}' from reported_symptoms")
        
        # Get new stats
        new_entropy = get_total_entropy(graph)
        context.context.current_entropy = new_entropy
        
        differentials = extract_differential_results(graph, top_n=5)
        
        # Store in context
        context.context.calculated_differentials = {
            d["condition_id"]: d["probability"] for d in differentials
        }
        
        return {
            "updated": True,
            "symptom": symptom_id,
            "value": value,
            "new_entropy": round(new_entropy, 3),
            "top_differentials": differentials[:3],
            "continue_questioning": new_entropy > 0.2,
            "note": "Graph updated and probabilities propagated" if new_entropy > 0.2 else "Entropy low enough - ready for final recommendation"
        }
        
    except Exception as e:
        print(f"Error updating graph: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "Graph update failed"
        }


@function_tool(
    name_override="assess_biopsy_indication",
    description_override="Calculate MRI fusion biopsy indication with evidence-based scoring"
)
def assess_biopsy_indication(
    context: RunContextWrapper[Any],
    pirads: int,
    psad: float,
    psa_velocity: float = None,
    lesion_size_mm: float = None
) -> Dict[str, Any]:
    """
    Assess indication for MRI fusion biopsy using evidence-based criteria
    
    :param pirads: PI-RADS score (1-5)
    :param psad: PSA density (ng/mL/cc)
    :param psa_velocity: PSA velocity (ng/mL/year), optional
    :param lesion_size_mm: Lesion size in mm, optional
    :return: Scoring with evidence citations and recommendations
    """
    try:
        from procedural.procedural_calculators import calculate_mri_fusion_indication
        
        fusion_available = context.context.__dict__.get("fusion_software_available", True)
        
        result = calculate_mri_fusion_indication(
            pirads=pirads,
            psad=psad,
            psa_velocity=psa_velocity,
            lesion_size_mm=lesion_size_mm,
            fusion_available=fusion_available
        )
        
        # Store in context
        context.context.mri_fusion_assessment = result
        
        return result
        
    except Exception as e:
        return {"error": str(e)}


@function_tool(
    name_override="assess_hifu_eligibility",
    description_override="Calculate HIFU focal therapy eligibility with evidence-based scoring"
)
def assess_hifu_eligibility(
    context: RunContextWrapper[Any],
    pirads: int,
    lesion_size_mm: float,
    gleason_score: str,
    prostate_volume_cc: float
) -> Dict[str, Any]:
    """
    Assess eligibility for HIFU focal therapy using evidence-based criteria
    
    :param pirads: PI-RADS score (1-5)
    :param lesion_size_mm: Lesion size in mm
    :param gleason_score: Gleason score string (e.g., "3+4", "4+3")
    :param prostate_volume_cc: Prostate volume in cubic centimeters
    :return: Scoring with evidence citations, contraindications, and cost estimates
    """
    try:
        from procedural.procedural_calculators import calculate_hifu_eligibility
        
        hifu_available = context.context.__dict__.get("hifu_available", False)
        
        result = calculate_hifu_eligibility(
            pirads=pirads,
            lesion_size_mm=lesion_size_mm,
            gleason_score=gleason_score,
            prostate_volume_cc=prostate_volume_cc,
            hifu_available=hifu_available
        )
        
        # Store in context
        context.context.hifu_assessment = result
        
        return result
        
    except Exception as e:
        return {"error": str(e)}


@function_tool(
    name_override="compare_treatment_options",
    description_override="Compare Active Surveillance vs Surgery using patient-specific factors and preferences"
)
def compare_treatment_options(
    context: RunContextWrapper[Any],
    age: int,
    psad: float,
    pirads: int,
    gleason_score: str,
    comorbidity: str,
    urinary_concern: float = 0.5,
    sexual_concern: float = 0.5,
    avoid_overtreatment: float = 0.5
) -> Dict[str, Any]:
    """
    Compare Active Surveillance vs Surgery with non-prescriptive scoring
    
    :param age: Patient age
    :param psad: PSA density
    :param pirads: PI-RADS score
    :param gleason_score: Gleason score
    :param comorbidity: "low", "moderate", or "high"
    :param urinary_concern: 0-1 scale of concern about urinary side effects
    :param sexual_concern: 0-1 scale of concern about sexual side effects
    :param avoid_overtreatment: 0-1 scale of preference to avoid unnecessary treatment
    :return: Comparative scores and recommendation
    """
    try:
        from procedural.procedural_calculators import calculate_active_surveillance_vs_surgery
        
        patient_preferences = {
            "urinary": urinary_concern,
            "sexual": sexual_concern,
            "avoid_overtreatment": avoid_overtreatment
        }
        
        result = calculate_active_surveillance_vs_surgery(
            age=age,
            psad=psad,
            pirads=pirads,
            gleason_score=gleason_score,
            comorbidity=comorbidity,
            patient_preferences=patient_preferences
        )
        
        # Store in context
        context.context.treatment_comparison = result
        
        return result
        
    except Exception as e:
        return {"error": str(e)}


@function_tool(
    name_override="generate_treatment_plan",
    description_override="Generate comprehensive treatment plan with pathways, booking recommendations, and patient materials"
)
def generate_treatment_plan(
    context: RunContextWrapper[Any]
) -> Dict[str, Any]:
    """
    Generate complete treatment plan summary including:
    - Treatment pathways with evidence
    - Booking recommendations
    - Patient email content
    - Clinical summary for EMR
    
    Requires previous calls to assessment tools
    :return: Complete treatment plan with patient and clinical materials
    """
    try:
        from procedural.procedural_calculators import generate_treatment_summary
        
        # Get assessments from context
        mri_result = context.context.__dict__.get("mri_fusion_assessment")
        hifu_result = context.context.__dict__.get("hifu_assessment")
        treatment_comparison = context.context.__dict__.get("treatment_comparison")
        
        if not all([mri_result, hifu_result, treatment_comparison]):
            return {
                "error": "Missing assessments. Call assess_biopsy_indication, assess_hifu_eligibility, and compare_treatment_options first."
            }
        
        # Compile patient data
        patient_data = {
            "age": context.context.age,
            "psa": context.context.__dict__.get("psa"),
            "psad": context.context.__dict__.get("psad"),
            "pirads": context.context.__dict__.get("pirads"),
            "gleason_score": context.context.__dict__.get("gleason_score"),
            "comorbidity": context.context.__dict__.get("comorbidity"),
            "preferences": {
                "urinary": context.context.__dict__.get("urinary_concern", 0.5),
                "sexual": context.context.__dict__.get("sexual_concern", 0.5),
                "avoid_overtreatment": context.context.__dict__.get("avoid_overtreatment", 0.5)
            }
        }
        
        # Generate comprehensive summary
        result = generate_treatment_summary(
            patient_data=patient_data,
            mri_fusion_result=mri_result,
            hifu_result=hifu_result,
            as_vs_surgery_result=treatment_comparison
        )
        
        # Store in context
        context.context.treatment_plan = result
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@function_tool(
    name_override="get_patient_education",
    description_override="Get educational content to explain medical concepts to patients (e.g., PSA, surgery options)"
)
def get_patient_education(
    context: RunContextWrapper[Any],
    topic: str
) -> Dict[str, Any]:
    """
    Retrieve patient-friendly educational content on medical topics.
    Useful for explaining test results, addressing concerns, or discussing options.
    
    :param topic: Topic to search for (e.g., "PSA", "BPH surgery", "elevated PSA")
    :return: Educational content with key points
    """
    try:
        from differentials.clinical_education import search_education_topics, get_education_content
        
        # Search for matching topics
        matches = search_education_topics(topic)
        
        if not matches:
            return {
                "found": False,
                "topic": topic,
                "note": "No specific educational content found for this topic"
            }
        
        # Get the first matching topic
        content = get_education_content(matches[0])
        
        return {
            "found": True,
            "title": content["title"],
            "short_answer": content["short_answer"],
            "key_points": content["key_points"],
            "full_content_available": True,
            "note": f"Use this to explain {topic} to the patient"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "note": "Failed to retrieve education content"
        }


@function_tool(
    name_override="generate_patient_action_plan",
    description_override="Generate comprehensive action plan with investigations and management recommendations"
)
def generate_patient_action_plan(
    context: RunContextWrapper[Any]
) -> Dict[str, Any]:
    """
    Generate a structured patient action plan based on the consultation.
    Includes patient info, differentials, investigations, and management plan.
    
    :return: Formatted action plan as markdown
    """
    try:
        from differentials.letter_generator import generate_action_plan
        from differentials.graph_builder import extract_differential_results
        from differentials.graph_engine import ProbabilityGraph
        
        # Get differentials from graph
        graph_dict = context.context.probability_graph
        if graph_dict:
            graph = ProbabilityGraph()
            graph.nodes = graph_dict["nodes"]
            graph.edges = graph_dict["edges"]
            differentials = extract_differential_results(graph, top_n=5)
        else:
            differentials = []
        
        # Collect recommended investigations
        investigations = []
        for diff in differentials[:3]:  # Top 3 conditions
            condition_id = diff.get("condition_id", "")
            # Check for investigation needs in urology
            if "uro_" in condition_id:
                from differentials.urology_conditions import get_required_investigations
                condition_key = condition_id.replace("uro_", "")
                investigations.extend(get_required_investigations(condition_key))
        
        # Remove duplicates
        investigations = list(set(investigations))
        
        # Generate action plan
        context_dict = {
            "age": context.context.age,
            "gender": context.context.gender,
            "chief_complaint": context.context.chief_complaint,
            "reported_symptoms": context.context.reported_symptoms,
            "medical_history": context.context.medical_history,
            "current_medications": context.context.current_medications,
            "allergies": context.context.allergies,
            "patient_concerns": context.context.patient_concerns,
            "consultation_goals": context.context.consultation_goals,
            "symptom_details": context.context.symptom_details
        }
        
        action_plan = generate_action_plan(context_dict, differentials, investigations)
        
        return {
            "success": True,
            "action_plan": action_plan,
            "note": "Action plan generated - present this to the patient"
        }
        
    except Exception as e:
        print(f"Error generating action plan: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "Failed to generate action plan"
        }


@function_tool(
    name_override="generate_gp_referral_letter",
    description_override="Generate formal GP referral letter summarizing the consultation"
)
def generate_gp_referral_letter(
    context: RunContextWrapper[Any]
) -> Dict[str, Any]:
    """
    Generate a formal GP referral letter with consultation summary.
    
    :return: Formatted GP letter
    """
    try:
        from differentials.letter_generator import generate_gp_letter
        from differentials.graph_builder import extract_differential_results
        from differentials.graph_engine import ProbabilityGraph
        
        # Get differentials
        graph_dict = context.context.probability_graph
        if graph_dict:
            graph = ProbabilityGraph()
            graph.nodes = graph_dict["nodes"]
            graph.edges = graph_dict["edges"]
            differentials = extract_differential_results(graph, top_n=3)
        else:
            differentials = []
        
        # Collect investigations
        investigations = []
        for diff in differentials:
            condition_id = diff.get("condition_id", "")
            if "uro_" in condition_id:
                from differentials.urology_conditions import get_required_investigations
                condition_key = condition_id.replace("uro_", "")
                investigations.extend(get_required_investigations(condition_key))
        
        investigations = list(set(investigations))
        
        # Generate letter
        context_dict = {
            "age": context.context.age,
            "gender": context.context.gender,
            "chief_complaint": context.context.chief_complaint,
            "narrative_summary": context.context.narrative_summary,
            "medical_history": context.context.medical_history,
            "current_medications": context.context.current_medications,
            "allergies": context.context.allergies,
            "patient_concerns": context.context.patient_concerns,
            "symptom_details": context.context.symptom_details
        }
        
        gp_letter = generate_gp_letter(context_dict, differentials, investigations)
        
        return {
            "success": True,
            "gp_letter": gp_letter,
            "note": "GP referral letter generated"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "note": "Failed to generate GP letter"
        }


@function_tool(
    name_override="score_procedural_pathway",
    description_override="Score patient for surgical/procedural pathways (biopsy, HIFU) based on clinical features"
)
def score_procedural_pathway(
    context: RunContextWrapper[Any],
    pirads: int | None = None,
    psad: float | None = None,
    psav: float | None = None,
    lesion_size_mm: int | None = None,
    prostate_volume_ml: int | None = None,
    gleason_max: int | None = None
) -> Dict[str, Any]:
    """
    Score patient for procedural pathways using clinical graph calculators.
    
    Uses YAML-based clinical graphs for:
    - MRI-fusion biopsy indications
    - Focal HIFU eligibility
    
    Routes to appropriate clinical role and provides evidence-based recommendations.
    
    :param pirads: PI-RADS score (1-5)
    :param psad: PSA density (ng/mL/cc)
    :param psav: PSA velocity (ng/mL/year)
    :param lesion_size_mm: Lesion size in mm
    :param prostate_volume_ml: Prostate volume in mL
    :param gleason_max: Maximum Gleason score
    :return: Procedural plan with routing and evidence
    """
    try:
        from procedural.scorer import decide_and_prepare, format_procedural_summary
        
        # Build features dict
        features = {}
        if pirads is not None:
            features["PIRADS"] = pirads
        if psad is not None:
            features["PSAD"] = psad
        if psav is not None:
            features["PSAV"] = psav
        if lesion_size_mm is not None:
            features["LESION"] = lesion_size_mm
        if prostate_volume_ml is not None:
            features["PROSTATE_VOL"] = prostate_volume_ml
        if gleason_max is not None:
            features["GLEASON_MAX"] = gleason_max
        
        # Get red flags from context
        red_flags = context.context.red_flags_present if hasattr(context.context, 'red_flags_present') else []
        
        # Score and route
        plan = decide_and_prepare(features, red_flags)
        
        # Format for display
        summary = format_procedural_summary(plan)
        
        return {
            "success": True,
            "plan": plan,
            "summary": summary,
            "assigned_role": plan["assigned_role"],
            "signoff_required": plan["signoff_required"],
            "note": "Procedural pathway scored - use this to explain options to patient"
        }
        
    except Exception as e:
        print(f"Error scoring procedural pathway: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "Failed to score procedural pathway"
        }
