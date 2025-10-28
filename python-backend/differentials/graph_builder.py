"""
Graph Builder
Constructs probability graphs from calculators
"""

from typing import Dict, Any, List
import random

# Mandatory Safety Questions for Urology
# These MUST be asked before entropy-driven questions
MANDATORY_SAFETY_QUESTIONS = [
    {
        "id": "blood_in_urine",
        "question": "Have you noticed any blood in your urine, even if just once?",
        "rationale": "Critical for ruling out bladder cancer, kidney stones, severe infection",
        "rules_out": ["bladder_cancer", "kidney_stones", "severe_infection"]
    },
    {
        "id": "severe_sudden_pain",
        "question": "Have you experienced any sudden, severe pain?",
        "rationale": "Critical for ruling out testicular torsion, kidney stone, acute retention",
        "rules_out": ["testicular_torsion", "kidney_stones", "acute_urinary_retention"]
    },
    {
        "id": "fever_unwell",
        "question": "Do you have a fever or feel generally very unwell?",
        "rationale": "Critical for ruling out sepsis, severe pyelonephritis",
        "rules_out": ["sepsis", "pyelonephritis", "severe_prostatitis"]
    },
    {
        "id": "weight_loss",
        "question": "Have you had any unexplained weight loss recently?",
        "rationale": "Red flag for malignancy",
        "rules_out": ["prostate_cancer", "bladder_cancer", "renal_cancer"]
    },
    {
        "id": "family_history_cancer",
        "question": "Does anyone in your immediate family have a history of prostate or bladder cancer?",
        "rationale": "Risk stratification for malignancy",
        "rules_out": ["prostate_cancer", "bladder_cancer"]
    }
]

from .graph_engine import ProbabilityGraph
# from .pain_conditions import PAIN_SYMPTOM_MATRIX  # Commented out - urology only
from .urology_conditions import UROLOGY_SYMPTOM_MATRIX


def build_graph_from_calculators() -> ProbabilityGraph:
    """
    Build initial probability graph from all available calculators.
    
    For now, we're a UROLOGY consultation service, so we only build urology graph.
    Future: Could detect domain and build appropriate graph.
    
    Returns:
        ProbabilityGraph with nodes and edges from all calculators
    """
    graph = ProbabilityGraph()
    
    # ONLY add urology condition nodes (we're a urology service)
    _add_urology_nodes(graph)
    
    # Future: Add domain detection
    # if domain == "throat": _add_infection_nodes(graph)
    # elif domain == "pain": _add_pain_nodes(graph)
    # elif domain == "urology": _add_urology_nodes(graph)
    
    return graph


def _add_infection_nodes(graph: ProbabilityGraph):
    """Add nodes and edges for infection/throat conditions"""
    
    # Symptom nodes
    symptoms = [
        "fever",
        "sore_throat",
        "tonsil_swelling",
        "lymph_nodes",
        "pus_on_tonsils",
        "cough",
        "runny_nose",
        "headache",
        "body_ache",
        "no_cough"  # Absence symptom
    ]
    
    for symptom in symptoms:
        graph.add_node(symptom, "symptom", value=None, label=symptom.replace("_", " ").title())
    
    # Disease nodes
    graph.add_node("strep_throat", "disease", probability=0.5, label="Strep Throat (Bacterial)")
    graph.add_node("viral_pharyngitis", "disease", probability=0.5, label="Viral Pharyngitis")
    graph.add_node("influenza", "disease", probability=0.3, label="Influenza")
    graph.add_node("common_cold", "disease", probability=0.3, label="Common Cold")
    
    # Edges: symptom → disease with weights
    # Strep throat (bacterial)
    graph.add_edge("fever", "strep_throat", 0.7)
    graph.add_edge("sore_throat", "strep_throat", 0.9)
    graph.add_edge("tonsil_swelling", "strep_throat", 0.85)
    graph.add_edge("lymph_nodes", "strep_throat", 0.8)
    graph.add_edge("pus_on_tonsils", "strep_throat", 0.9)
    graph.add_edge("no_cough", "strep_throat", 0.7)  # Absence of cough favors bacterial
    
    # Viral pharyngitis
    graph.add_edge("sore_throat", "viral_pharyngitis", 0.8)
    graph.add_edge("cough", "viral_pharyngitis", 0.6)
    graph.add_edge("runny_nose", "viral_pharyngitis", 0.7)
    graph.add_edge("headache", "viral_pharyngitis", 0.5)
    
    # Influenza
    graph.add_edge("fever", "influenza", 0.9)
    graph.add_edge("body_ache", "influenza", 0.85)
    graph.add_edge("headache", "influenza", 0.7)
    graph.add_edge("sore_throat", "influenza", 0.5)
    
    # Common cold
    graph.add_edge("runny_nose", "common_cold", 0.9)
    graph.add_edge("cough", "common_cold", 0.7)
    graph.add_edge("sore_throat", "common_cold", 0.6)


def _add_pain_nodes(graph: ProbabilityGraph):
    """Add nodes and edges for pain/musculoskeletal conditions"""
    
    # Common pain symptoms
    pain_symptoms = [
        "joint_pain",
        "swelling",
        "stiffness",
        "redness",
        "warmth",
        "deformity",
        "limited_range",
        "fatigue",
        "weight_loss",
        "nodules",
        "bone_pain",
        "muscle_weakness",
        "numbness_tingling"
    ]
    
    for symptom in pain_symptoms:
        if symptom not in graph.nodes:
            graph.add_node(symptom, "symptom", value=None, label=symptom.replace("_", " ").title())
    
    # Add disease nodes from pain matrix
    # COMMENTED OUT - urology only for now
    # for condition_id, condition_data in PAIN_SYMPTOM_MATRIX.items():
    #     disease_id = f"pain_{condition_id}"
    #     graph.add_node(
    #         disease_id,
    #         "disease",
    #         probability=0.3,
    #         label=condition_data["name"]
    #     )
    #     
    #     # Add edges from symptoms to this condition
    #     for symptom_def in condition_data["symptoms"]:
    #         symptom_id = symptom_def["id"]
    #         weight = symptom_def["weight"]
    #         
    #         # Ensure symptom node exists
    #         if symptom_id not in graph.nodes:
    #             graph.add_node(symptom_id, "symptom", value=None, label=symptom_def["label"])
    #         
    #         graph.add_edge(symptom_id, disease_id, weight)


def _add_urology_nodes(graph: ProbabilityGraph):
    """Add nodes and edges for urological conditions"""
    
    # Add disease nodes from urology matrix
    for condition_id, condition_data in UROLOGY_SYMPTOM_MATRIX.items():
        disease_id = f"uro_{condition_id}"
        graph.add_node(
            disease_id,
            "disease",
            probability=0.3,
            label=condition_data["name"]
        )
        
        # Add edges from symptoms to this condition
        for symptom_def in condition_data["symptoms"]:
            symptom_id = symptom_def["id"]
            weight = symptom_def["weight"]
            
            # Ensure symptom node exists
            if symptom_id not in graph.nodes:
                graph.add_node(symptom_id, "symptom", value=None, label=symptom_def["label"])
            
            graph.add_edge(symptom_id, disease_id, weight)


def populate_graph_from_context(graph: ProbabilityGraph, context: Dict[str, Any]) -> ProbabilityGraph:
    """
    Populate graph with known symptoms and patient data from context
    
    Args:
        graph: Empty or base graph
        context: Clinical context with reported_symptoms, age, etc.
    
    Returns:
        Graph with initial values populated
    """
    # Mark known symptoms as present
    reported_symptoms = context.get("reported_symptoms", [])
    
    print(f"DEBUG populate_graph_from_context: reported_symptoms = {reported_symptoms}")
    print(f"DEBUG populate_graph_from_context: graph has {len(graph.nodes)} nodes")
    print(f"DEBUG populate_graph_from_context: available symptom nodes = {[n for n, d in graph.nodes.items() if d['type'] == 'symptom'][:10]}")
    
    for symptom_text in reported_symptoms:
        # Normalize symptom text to node IDs
        symptom_id = symptom_text.lower().replace(" ", "_")
        
        print(f"DEBUG populate_graph_from_context: Looking for symptom_id '{symptom_id}' in graph...")
        
        if symptom_id in graph.nodes:
            graph.nodes[symptom_id]["value"] = 1.0
            print(f"DEBUG populate_graph_from_context: ✅ Found and populated '{symptom_id}' with value 1.0")
        else:
            print(f"DEBUG populate_graph_from_context: ❌ NOT FOUND: '{symptom_id}' not in graph.nodes")
    
    return graph


def extract_differential_results(graph: ProbabilityGraph, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Extract top differential diagnoses from graph
    
    Args:
        graph: Probability graph
        top_n: Number of top conditions to return
    
    Returns:
        List of conditions with probabilities, sorted by likelihood
    """
    disease_nodes = [
        {
            "condition": node["label"],
            "condition_id": node["id"],
            "probability": node.get("probability", 0.5),
            "percentage": round(node.get("probability", 0.5) * 100, 1)
        }
        for node in graph.nodes.values()
        if node["type"] == "disease"
    ]
    
    # Sort by probability
    disease_nodes.sort(key=lambda x: x["probability"], reverse=True)
    
    return disease_nodes[:top_n]


def format_siqorstaa_question(symptom_id: str, symptom_label: str) -> str:
    """
    Format a symptom into a proper SIQORSTAA-style question
    
    Args:
        symptom_id: Internal symptom ID
        symptom_label: Human-readable label
    
    Returns:
        Formatted question string
    """
    # Map symptom types to question templates
    if "pain" in symptom_id or "ache" in symptom_id:
        return f"On a scale of 0-10, how severe is your {symptom_label.lower()}?"
    
    if "swelling" in symptom_id or "swollen" in symptom_label.lower():
        return f"Do you have {symptom_label.lower()}? If yes, how pronounced is it (0-10)?"
    
    if "fever" in symptom_id:
        return f"Do you have a fever? If yes, what is your temperature?"
    
    if "cough" in symptom_id:
        return f"Do you have a cough?"
    
    # Default yes/no question
    return f"Do you have {symptom_label.lower()}?"
