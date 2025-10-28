"""
CLEAN TOOLS - Urology Pathway Only
Minimal tools focused on the urology calculator workflow
"""

import json
from agents import function_tool, RunContextWrapper
from py_mini_racer import MiniRacer
from typing import Dict, Any, List

# =============================================================================
# RED FLAG SAFETY CHECK (ONE QUESTION)
# =============================================================================

@function_tool(
    name_override="get_red_flag_checklist",
    description_override="Get the complete red flag checklist to ask as ONE question"
)
def get_red_flag_checklist(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Returns the complete list of red flags to ask about in ONE question.
    PI Agent should ask: "Do you have any of the following? If so, which ones?"
    
    :return: Dict with red flag checklist and interpretation guide
    """
    
    red_flags = [
        {
            "id": "blood_in_urine",
            "text": "Blood in your urine (red, pink, or brown urine)",
            "severity": 5,
            "action_if_yes": "Urgent urology referral - possible bladder cancer or stones"
        },
        {
            "id": "severe_sudden_pain",
            "text": "Severe sudden pain in testicles, groin, or lower abdomen",
            "severity": 5,
            "action_if_yes": "A&E immediately - possible torsion or acute retention"
        },
        {
            "id": "fever_feeling_unwell",
            "text": "Fever, chills, or feeling generally unwell",
            "severity": 4,
            "action_if_yes": "Urgent GP/A&E - possible infection or sepsis"
        },
        {
            "id": "unable_to_urinate",
            "text": "Unable to pass urine at all (acute retention)",
            "severity": 5,
            "action_if_yes": "A&E immediately - requires catheterization"
        },
        {
            "id": "unexplained_weight_loss",
            "text": "Unexplained weight loss (>10 lbs / 5 kg in 3 months)",
            "severity": 4,
            "action_if_yes": "2-week-wait cancer pathway referral"
        },
        {
            "id": "family_history_prostate_cancer",
            "text": "Family history of prostate cancer (father, brother)",
            "severity": 3,
            "action_if_yes": "Increases risk 2-3x - affects prior probability"
        },
        {
            "id": "previous_kidney_stones",
            "text": "Previous history of kidney stones",
            "severity": 2,
            "action_if_yes": "50% recurrence risk - affects prior probability"
        }
    ]
    
    # Store in context for later use
    context.context.red_flags_checked = True
    
    return {
        "red_flags": red_flags,
        "instruction_to_agent": "Ask patient: 'Do you have any of the following? If so, which ones?' then list all items.",
        "total_count": len(red_flags)
    }


@function_tool(
    name_override="record_red_flag_answers",
    description_override="Record which red flags patient reported (if any)"
)
def record_red_flag_answers(
    context: RunContextWrapper[Any],
    reported_flags: List[str] = None
) -> Dict[str, Any]:
    """
    Records which red flags the patient reported.
    
    :param reported_flags: List of red flag IDs patient mentioned (e.g., ["blood_in_urine", "fever_feeling_unwell"])
    :return: Dict with severity assessment and recommended action
    """
    
    if reported_flags is None:
        reported_flags = []
    
    # Store in context
    context.context.red_flags_present = reported_flags
    
    # Map flags to actions
    FLAG_DATA = {
        "blood_in_urine": {"severity": 5, "action": "Urgent urology referral", "affects_calc": True},
        "severe_sudden_pain": {"severity": 5, "action": "A&E immediately", "affects_calc": True},
        "fever_feeling_unwell": {"severity": 4, "action": "Urgent GP/A&E", "affects_calc": True},
        "unable_to_urinate": {"severity": 5, "action": "A&E immediately", "affects_calc": False},
        "unexplained_weight_loss": {"severity": 4, "action": "2WW cancer referral", "affects_calc": True},
        "family_history_prostate_cancer": {"severity": 3, "action": "Note for calculator", "affects_calc": True},
        "previous_kidney_stones": {"severity": 2, "action": "Note for calculator", "affects_calc": True}
    }
    
    # Determine highest severity
    max_severity = 0
    urgent_action_needed = False
    calculator_relevant_flags = []
    
    for flag_id in reported_flags:
        if flag_id in FLAG_DATA:
            flag_data = FLAG_DATA[flag_id]
            if flag_data["severity"] > max_severity:
                max_severity = flag_data["severity"]
            if flag_data["severity"] >= 5:
                urgent_action_needed = True
            if flag_data["affects_calc"]:
                calculator_relevant_flags.append(flag_id)
    
    # Update context with calculator-relevant data
    if "family_history_prostate_cancer" in reported_flags:
        context.context.__dict__["family_history_prostate_cancer"] = True
    if "previous_kidney_stones" in reported_flags:
        context.context.__dict__["previous_kidney_stones"] = True
    if "blood_in_urine" in reported_flags:
        context.context.__dict__["hematuria"] = True
        if "blood_in_urine" not in context.context.reported_symptoms:
            context.context.reported_symptoms.append("blood_in_urine")
    if "fever_feeling_unwell" in reported_flags:
        context.context.__dict__["fever_present"] = True
        if "fever" not in context.context.reported_symptoms:
            context.context.reported_symptoms.append("fever")
    
    return {
        "reported_count": len(reported_flags),
        "reported_flags": reported_flags,
        "highest_severity": max_severity,
        "urgent_action_needed": urgent_action_needed,
        "message_to_agent": "STOP - urgent referral needed" if urgent_action_needed else "Safe to proceed with diagnostic questions",
        "calculator_updates": calculator_relevant_flags
    }


# =============================================================================
# UROLOGY CALCULATOR (CORE)
# =============================================================================

@function_tool(
    name_override="build_probability_graph",
    description_override="Build probability graph using Bayesian calculator with evidence-based priors"
)
def build_probability_graph(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Build probability graph using the real Bayesian calculator (urology_calculator.py)
    
    :return: Dictionary with probabilities, graph structure, and clinical recommendations
    """
    try:
        from differentials.urology_calculator import compute_urology_differential, calculate_entropy
        from differentials.graph_engine import ProbabilityGraph
        
        print(f"DEBUG build_probability_graph: Starting with reported_symptoms = {context.context.reported_symptoms}")
        
        # Prepare symptoms dict for calculator
        symptoms = {
            "onset_speed": context.context.__dict__.get("onset_speed"),
            "fever_present": context.context.__dict__.get("fever_present", False),
            "dysuria": context.context.__dict__.get("dysuria", False),
            "hematuria": context.context.__dict__.get("hematuria", False),
            "reported_symptoms": context.context.reported_symptoms,
            "dysuria_severity": context.context.__dict__.get("dysuria_severity", 0),
            "weak_stream_severity": context.context.__dict__.get("weak_stream_severity", 0),
            "pain_severity": context.context.__dict__.get("pain_severity", 0),
            "nocturia_per_night": context.context.__dict__.get("nocturia_per_night", 0),
            "previous_kidney_stones": context.context.__dict__.get("previous_kidney_stones", False)
        }
        
        patient_info = {
            "age": context.context.age or 50,
            "gender": context.context.gender or "unknown",
            "family_history_prostate_cancer": context.context.__dict__.get("family_history_prostate_cancer", False),
            "previous_kidney_stones": context.context.__dict__.get("previous_kidney_stones", False)
        }
        
        print(f"DEBUG build_probability_graph: Calling calculator with symptoms={symptoms}, patient_info={patient_info}")
        
        # Call the REAL Bayesian calculator
        result = compute_urology_differential(symptoms, patient_info)
        
        print(f"DEBUG build_probability_graph: Calculator returned probabilities = {result['probabilities']}")
        
        # Calculate entropy
        entropy = calculate_entropy(result["probabilities"])
        context.context.current_entropy = entropy
        
        # Store graph in context with entropy metadata (for FindPivots to use)
        graph = result["graph"]
        if "nodes" not in graph:
            graph["nodes"] = {}
        graph["nodes"]["_metadata"] = {
            "type": "metadata",
            "entropy": entropy
        }
        context.context.probability_graph = graph
        
        # Format top differentials
        sorted_probs = sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True)
        top_differentials = [
            {
                "condition": cond,
                "probability": round(prob * 100, 1),
                "label": cond.replace("_", " ").title()
            }
            for cond, prob in sorted_probs[:5]
        ]
        
        # Get graph structure
        graph = result["graph"]
        
        return {
            "success": True,
            "probabilities": {k: round(v * 100, 1) for k, v in result["probabilities"].items()},
            "graph_structure": {
                "total_nodes": len(graph["nodes"]),
                "total_edges": len(graph["edges"]),
                "symptom_nodes": len([n for n in graph["nodes"].values() if n["type"] == "symptom"]),
                "disease_nodes": len([n for n in graph["nodes"].values() if n["type"] == "disease"])
            },
            "initial_entropy": round(entropy, 3),
            "top_differentials": top_differentials,
            "recommendation": result["recommendation"],
            "data_sources": result["citations"],
            "note": f"Bayesian graph built. Entropy: {entropy:.3f}. Top: {sorted_probs[0][0]} ({sorted_probs[0][1]:.1%})"
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
    
    :param max_questions: Maximum number of questions to suggest
    :return: Dictionary with suggested questions ranked by information gain
    """
    try:
        from differentials.graph_engine import ProbabilityGraph, find_pivots, choose_next_question, expected_information_gain
        
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
        
        # Expand working set to include symptoms connected to diseases
        # FindPivots returns disease nodes, but we need symptom nodes to ask about
        expanded_working_set = set()
        for node_id in working_set:
            node = graph.nodes.get(node_id, {})
            if node.get("type") == "symptom":
                expanded_working_set.add(node_id)
            elif node.get("type") == "disease":
                # Find symptoms that connect to this disease
                for edge in graph.edges:
                    if edge["to"] == node_id and graph.nodes.get(edge["from"], {}).get("type") == "symptom":
                        expanded_working_set.add(edge["from"])
        
        working_set = expanded_working_set
        print(f"DEBUG find_strategic_questions: Expanded working set to symptoms: {working_set}")
        
        # Store pivot nodes in context
        context.context.pivot_nodes = list(pivots)
        
        # Prepare context data for information gain calculation
        current_symptoms = {
            "onset_speed": context.context.__dict__.get("onset_speed"),
            "fever_present": context.context.__dict__.get("fever_present", False),
            "dysuria": context.context.__dict__.get("dysuria", False),
            "hematuria": context.context.__dict__.get("hematuria", False),
            "reported_symptoms": context.context.reported_symptoms,
            "dysuria_severity": context.context.__dict__.get("dysuria_severity", 0),
            "weak_stream_severity": context.context.__dict__.get("weak_stream_severity", 0),
            "pain_severity": context.context.__dict__.get("pain_severity", 0),
            "nocturia_per_night": context.context.__dict__.get("nocturia_per_night", 0),
        }
        
        patient_info = {
            "age": context.context.age or 50,
            "gender": context.context.gender or "unknown",
            "family_history_prostate_cancer": context.context.__dict__.get("family_history_prostate_cancer", False),
            "previous_kidney_stones": context.context.__dict__.get("previous_kidney_stones", False)
        }
        
        # Find best questions within working set
        questions = []
        checked = set(known_symptoms)  # Don't ask about known symptoms
        
        for _ in range(max_questions):
            next_symptom = choose_next_question(graph, working_set)
            if not next_symptom or next_symptom in checked:
                break
            
            checked.add(next_symptom)
            node = graph.nodes.get(next_symptom, {})
            gain = expected_information_gain(graph, next_symptom, current_symptoms, patient_info)
            
            print(f"DEBUG find_strategic_questions: Suggesting symptom={next_symptom}, gain={gain}")
            
            # Format question based on symptom type
            if "severity" in next_symptom or next_symptom in ["dysuria_severity", "weak_stream_severity", "pain_severity"]:
                base = next_symptom.replace("_severity", "").replace("_", " ")
                question = f"On a scale of 0-10, how severe is the {base}?"
                qtype = "scale_0_10"
            elif next_symptom == "onset_speed":
                question = "Did your symptoms start suddenly (hours/days) or gradually (weeks/months)?"
                qtype = "choice"
            elif next_symptom == "nocturia_per_night":
                question = "How many times do you wake up at night to urinate?"
                qtype = "number"
            else:
                label = node.get("label", next_symptom.replace("_", " "))
                question = f"Do you have {label.lower()}?"
                qtype = "yes_no"
            
            questions.append({
                "symptom_id": next_symptom,
                "question": question,
                "information_gain": round(gain, 3),
                "type": qtype
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
    value: str
) -> Dict[str, Any]:
    """
    Update the probability graph with the patient's answer to a question.
    
    :param symptom_id: ID of the symptom (e.g., "weak_stream", "onset_speed")
    :param value: Patient's answer (True/False for yes/no, string for choices, 0-10 for severity)
    :return: Updated graph state and new differential probabilities
    """
    try:
        # Map symptom_id to the key used by the calculator
        symptom_key_mapping = {
            "fever": "fever_present",
            "pain_burning": "dysuria",
            "blood_in_urine": "hematuria"
        }
        
        # Use mapped key if available, otherwise use symptom_id as-is
        storage_key = symptom_key_mapping.get(symptom_id, symptom_id)
        
        # Store answer in context using the CORRECT key
        context.context.__dict__[storage_key] = value
        print(f"DEBUG update_graph_with_answer: Stored {storage_key}={value} in context")
        
        # If severity-related, ensure it's stored as numeric
        if "severity" in storage_key or storage_key in ["nocturia_per_night", "pain_severity"]:
            try:
                context.context.__dict__[storage_key] = int(value) if isinstance(value, str) else value
            except:
                context.context.__dict__[storage_key] = value
        
        # Remove from reported_symptoms if it was there (now answered)
        if symptom_id in context.context.reported_symptoms:
            context.context.reported_symptoms.remove(symptom_id)
            print(f"DEBUG update_graph_with_answer: Removed '{symptom_id}' from reported_symptoms")
        
        # Recalculate with new info using the calculator directly
        from differentials.urology_calculator import compute_urology_differential, calculate_entropy
        
        symptoms = {
            "onset_speed": context.context.__dict__.get("onset_speed"),
            "fever_present": context.context.__dict__.get("fever_present", False),
            "dysuria": context.context.__dict__.get("dysuria", False),
            "hematuria": context.context.__dict__.get("hematuria", False),
            "reported_symptoms": context.context.reported_symptoms,
            "dysuria_severity": context.context.__dict__.get("dysuria_severity", 0),
            "weak_stream_severity": context.context.__dict__.get("weak_stream_severity", 0),
            "pain_severity": context.context.__dict__.get("pain_severity", 0),
            "nocturia_per_night": context.context.__dict__.get("nocturia_per_night", 0),
            "previous_kidney_stones": context.context.__dict__.get("previous_kidney_stones", False)
        }
        
        patient_info = {
            "age": context.context.age or 50,
            "gender": context.context.gender or "unknown",
            "family_history_prostate_cancer": context.context.__dict__.get("family_history_prostate_cancer", False),
            "previous_kidney_stones": context.context.__dict__.get("previous_kidney_stones", False)
        }
        
        result = compute_urology_differential(symptoms, patient_info)
        new_entropy = calculate_entropy(result["probabilities"])
        context.context.current_entropy = new_entropy
        
        # Store updated graph in context
        graph = result["graph"]
        if "nodes" not in graph:
            graph["nodes"] = {}
        graph["nodes"]["_metadata"] = {"type": "metadata", "entropy": new_entropy}
        
        # CRITICAL: Mark BOTH the UI symptom_id AND the calculator key in the graph
        # This prevents the question from being asked again
        
        # Mark the original symptom_id (e.g., "fever") if it exists in graph
        if symptom_id in graph["nodes"]:
            graph["nodes"][symptom_id]["value"] = value
            print(f"DEBUG update_graph_with_answer: Marked {symptom_id} with value={value} in graph")
        
        # Mark the mapped calculator key (e.g., "fever_present") if different
        if storage_key != symptom_id and storage_key in graph["nodes"]:
            graph["nodes"][storage_key]["value"] = value
            print(f"DEBUG update_graph_with_answer: Also marked calculator key {storage_key} with value={value}")
        
        context.context.probability_graph = graph
        
        # Track questions asked
        if not hasattr(context.context, 'questions_asked'):
            context.context.questions_asked = 0
        context.context.questions_asked += 1
        
        # Get top differentials
        sorted_probs = sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True)
        top_diffs = [
            {
                "condition": cond,
                "probability": round(prob * 100, 1),
                "label": cond.replace("_", " ").title()
            }
            for cond, prob in sorted_probs[:3]
        ]
        
        return {
            "updated": True,
            "symptom": symptom_id,
            "value": value,
            "new_entropy": round(new_entropy, 3),
            "top_differentials": top_diffs,
            "continue_questioning": new_entropy > 0.2,
            "note": "Graph updated and probabilities recalculated" if new_entropy > 0.2 else "Entropy low enough - ready for final recommendation"
        }
        
    except Exception as e:
        print(f"Error updating graph: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "note": "Graph update failed"
        }


# =============================================================================
# FINAL OUTPUT GENERATION
# =============================================================================

@function_tool(
    name_override="generate_patient_action_plan",
    description_override="Generate comprehensive action plan with investigations and management recommendations"
)
def generate_patient_action_plan(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Generate comprehensive patient action plan based on differential diagnosis.
    """
    try:
        from differentials.urology_calculator import compute_urology_differential
        
        # Get final probabilities
        symptoms = {
            "reported_symptoms": context.context.reported_symptoms,
            "onset_speed": context.context.__dict__.get("onset_speed"),
            "fever_present": context.context.__dict__.get("fever_present", False),
            "dysuria": context.context.__dict__.get("dysuria", False),
            "hematuria": context.context.__dict__.get("hematuria", False)
        }
        
        patient_info = {
            "age": context.context.age or 50,
            "gender": context.context.gender or "unknown"
        }
        
        result = compute_urology_differential(symptoms, patient_info)
        
        return {
            "patient_summary": {
                "age": context.context.age,
                "gender": context.context.gender,
                "chief_complaint": context.context.chief_complaint or "Urinary symptoms"
            },
            "differential_diagnoses": result["probabilities"],
            "recommendation": result["recommendation"],
            "next_steps": [
                "Book GP appointment for examination",
                "Urine dipstick and culture",
                "Consider PSA test if age >50 and male",
                "Ultrasound if hematuria present"
            ]
        }
        
    except Exception as e:
        print(f"Error generating action plan: {e}")
        return {"error": str(e)}


@function_tool(
    name_override="generate_gp_referral_letter",
    description_override="Generate formal GP referral letter summarizing the consultation"
)
def generate_gp_referral_letter(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Generate GP referral letter.
    """
    
    from datetime import datetime
    
    letter = f"""
Dear Dr [GP Name],

RE: {context.context.age}-year-old {context.context.gender} - Urology Consultation Summary

Date: {datetime.now().strftime("%d/%m/%Y")}

**Chief Complaint:**
{context.context.chief_complaint or "Urinary symptoms"}

**Presenting Symptoms:**
{", ".join(context.context.reported_symptoms)}

**Red Flags Assessed:**
{"None reported" if not context.context.red_flags_present else ", ".join(context.context.red_flags_present)}

**Differential Diagnoses:**
[Top differentials from calculator]

**Recommended Investigations:**
- Urine dipstick and MC&S
- PSA (if male >50)
- Renal function (U&E)
- Consider imaging if hematuria present

**Management Plan:**
[From calculator recommendation]

**Action Required:**
Please arrange the above investigations and consider referral to urology if red flags present.

Yours sincerely,
[Consultant Urologist]
    """
    
    return {
        "letter": letter.strip(),
        "format": "text",
        "ready_to_send": True
    }


# =============================================================================
# TREATMENT PATHWAY (For Treatment Agent - Separate)
# =============================================================================

@function_tool(
    name_override="score_procedural_pathway",
    description_override="Score patient for surgical/procedural pathways (biopsy, HIFU) based on clinical features"
)
def score_procedural_pathway(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Score patient for surgical/procedural pathways.
    Used by Treatment Agent, not diagnostic agents.
    """
    try:
        from procedural.procedural_calculators import (
            assess_biopsy_indication,
            assess_hifu_eligibility
        )
        
        # This is for LATER in the pathway (not diagnostic)
        patient_data = {
            "age": context.context.age,
            "psa": context.context.__dict__.get("psa"),
            "pirads": context.context.__dict__.get("pirads")
        }
        
        biopsy_result = assess_biopsy_indication(patient_data)
        hifu_result = assess_hifu_eligibility(patient_data)
        
        return {
            "biopsy_indication": biopsy_result,
            "hifu_eligibility": hifu_result
        }
        
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# PROCEDURE EDUCATION TOOLS
# =============================================================================

@function_tool(
    name_override="get_procedure_education",
    description_override="Get detailed patient education about a specific prostate procedure"
)
def get_procedure_education(context: RunContextWrapper[Any], procedure_name: str) -> Dict[str, Any]:
    """
    Fetch detailed education content about a prostate procedure for patient discussion.
    
    :param context: Runtime context
    :param procedure_name: One of: "mri_fusion_biopsy", "hifu", "active_surveillance", 
                           "radical_prostatectomy", "radiation_therapy"
    :return: Dict with procedure details, recovery, side effects, evidence
    """
    import os
    
    procedure_file = f"procedures/procedure_education.md"
    
    try:
        if not os.path.exists(procedure_file):
            return {
                "error": f"Procedure file not found: {procedure_file}",
                "available_procedures": [
                    "mri_fusion_biopsy",
                    "hifu", 
                    "active_surveillance",
                    "radical_prostatectomy",
                    "radiation_therapy"
                ]
            }
        
        with open(procedure_file, 'r') as f:
            content = f.read()
        
        # Extract the section for the requested procedure
        procedure_map = {
            "mri_fusion_biopsy": "## MRI-Fusion Biopsy",
            "hifu": "## HIFU (High-Intensity Focused Ultrasound)",
            "active_surveillance": "## Active Surveillance",
            "radical_prostatectomy": "## Radical Prostatectomy (Surgery)",
            "radiation_therapy": "## Radiation Therapy"
        }
        
        if procedure_name.lower() not in procedure_map:
            return {
                "error": f"Unknown procedure: {procedure_name}",
                "available_procedures": list(procedure_map.keys())
            }
        
        # Find and extract the section
        start_marker = procedure_map[procedure_name.lower()]
        start_idx = content.find(start_marker)
        
        if start_idx == -1:
            return {"error": f"Procedure section not found: {procedure_name}"}
        
        # Find the next section (##) or end of file
        next_section = content.find("\n## ", start_idx + 1)
        if next_section == -1:
            section_content = content[start_idx:]
        else:
            section_content = content[start_idx:next_section]
        
        return {
            "procedure": procedure_name,
            "content": section_content,
            "formatted": True
        }
        
    except Exception as e:
        return {"error": f"Failed to load procedure education: {str(e)}"}


@function_tool(
    name_override="get_procedure_comparison",
    description_override="Get comparison table of prostate cancer treatment options"
)
def get_procedure_comparison(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """
    Fetch the procedure comparison table for discussing treatment options with patient.
    
    :param context: Runtime context
    :return: Dict with comparison table and decision framework
    """
    import os
    
    comparison_file = "procedures/procedure_comparison_table.md"
    
    try:
        if not os.path.exists(comparison_file):
            return {"error": f"Comparison file not found: {comparison_file}"}
        
        with open(comparison_file, 'r') as f:
            content = f.read()
        
        return {
            "content": content,
            "formatted": True,
            "use_case": "Present this table when discussing treatment options with patient"
        }
        
    except Exception as e:
        return {"error": f"Failed to load procedure comparison: {str(e)}"}
