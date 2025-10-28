"""
Graph Reasoning Engine - FindPivots Algorithm & Entropy Calculations
Based on bounded propagation for efficient probabilistic reasoning
"""
from typing import Dict, List, Set, Tuple, Any
import math


class ProbabilityGraph:
    """Represents a probabilistic reasoning graph with nodes and edges"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
    
    def add_node(self, node_id: str, node_type: str, **kwargs):
        """Add a node to the graph"""
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "value": kwargs.get("value"),
            "probability": kwargs.get("probability", 0.5),
            **kwargs
        }
    
    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0):
        """Add a weighted edge"""
        self.edges.append({
            "from": from_id,
            "to": to_id,
            "weight": weight
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Export graph as dictionary"""
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }


def find_pivots(
    graph: ProbabilityGraph,
    seed_set: List[str],
    B: float = 1.0,
    k: int = 3
) -> Tuple[Set[str], Set[str]]:
    """
    FindPivots algorithm - identifies pivotal nodes for efficient propagation
    
    Args:
        graph: Probability graph
        seed_set: Initial complete nodes (symptoms with known values)
        B: Distance/uncertainty bound
        k: Relaxation depth (number of propagation steps)
    
    Returns:
        (pivots, working_set) tuple where:
        - pivots: Minimal set of strategic nodes
        - working_set: All nodes reached within bound B
    """
    # Initialize distances
    bd = {node_id: float('inf') for node_id in graph.nodes.keys()}
    for s in seed_set:
        bd[s] = 0.0
    
    W = set(seed_set)
    Wi = set(seed_set)
    
    # Relax for k steps
    for i in range(1, k + 1):
        next_Wi = set()
        
        for edge in graph.edges:
            if edge["from"] in Wi:
                weight = edge.get("weight", 1.0)
                candidate = bd[edge["from"]] + weight
                
                if candidate <= bd[edge["to"]]:
                    bd[edge["to"]] = candidate
                    
                    if candidate < B:
                        next_Wi.add(edge["to"])
                        W.add(edge["to"])
        
        if not next_Wi:
            break
        
        Wi = next_Wi
        
        # Early stopping if expansion too large
        if len(W) > k * len(seed_set):
            return set(seed_set), W
    
    # Build forest F of relaxed edges
    F = [
        e for e in graph.edges
        if e["from"] in W and e["to"] in W
        and bd[e["to"]] == bd[e["from"]] + e.get("weight", 1.0)
    ]
    
    # Group edges into trees by parent
    children: Dict[str, List[str]] = {}
    for e in F:
        if e["from"] not in children:
            children[e["from"]] = []
        children[e["from"]].append(e["to"])
    
    # Find pivots (roots with >= k vertices)
    visited = set()
    pivots = set()
    
    for root in seed_set:
        count = 0
        stack = [root]
        
        while stack:
            n = stack.pop()
            if n in visited:
                continue
            visited.add(n)
            count += 1
            
            if n in children:
                stack.extend(children[n])
        
        if count >= k:
            pivots.add(root)
    
    return pivots, W


def calculate_entropy(p: float) -> float:
    """
    Calculate Shannon entropy for a probability
    
    Args:
        p: Probability (0-1)
    
    Returns:
        Entropy value (0 = certain, 1 = maximum uncertainty at p=0.5)
    """
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def expected_information_gain(
    graph: ProbabilityGraph,
    symptom_id: str,
    current_context: dict = None,
    patient_info: dict = None
) -> float:
    """
    Calculate expected information gain from asking about a symptom
    Uses the REAL calculator with priors to simulate outcomes
    
    Args:
        graph: Probability graph (contains current probabilities)
        symptom_id: ID of symptom to query
        current_context: Current symptom values from context
        patient_info: Patient age, gender, etc for priors
    
    Returns:
        Expected entropy reduction (higher = more informative)
    """
    from .urology_calculator import compute_urology_differential, calculate_entropy as calc_entropy
    
    # Get current entropy from graph metadata
    current_entropy = graph.nodes.get("_metadata", {}).get("entropy", 2.0)
    
    # Map graph symptom names to calculator symptom names
    symptom_map = {
        "pain_burning": "dysuria",
        "blood_in_urine": "hematuria",
        "fever": "fever_present",
    }
    
    # Get the calculator symptom name
    calc_symptom = symptom_map.get(symptom_id, symptom_id)
    
    # Prepare current symptoms and patient info for calculator
    symptoms = current_context or {}
    patient = patient_info or {"age": 50, "gender": "unknown"}
    
    # Simulate: What if this symptom is TRUE?
    symptoms_if_yes = symptoms.copy()
    if "severity" in calc_symptom:
        symptoms_if_yes[calc_symptom] = 70  # Moderate severity
    elif calc_symptom == "nocturia_per_night":
        symptoms_if_yes[calc_symptom] = 3
    else:
        symptoms_if_yes[calc_symptom] = True
    
    try:
        result_yes = compute_urology_differential(symptoms_if_yes, patient)
        entropy_yes = calc_entropy(result_yes["probabilities"])
    except Exception as e:
        print(f"ERROR calculating entropy_yes for {symptom_id}: {e}")
        return 0.0
    
    # Simulate: What if this symptom is FALSE?
    symptoms_if_no = symptoms.copy()
    symptoms_if_no[calc_symptom] = False if "severity" not in calc_symptom else 0
    
    try:
        result_no = compute_urology_differential(symptoms_if_no, patient)
        entropy_no = calc_entropy(result_no["probabilities"])
    except Exception as e:
        print(f"ERROR calculating entropy_no for {symptom_id}: {e}")
        return 0.0
    
    # Expected entropy (assume 50/50 yes/no)
    expected_entropy = 0.5 * (entropy_yes + entropy_no)
    
    # Information gain = reduction in entropy
    gain = current_entropy - expected_entropy
    
    print(f"DEBUG expected_information_gain: symptom={symptom_id}, current={current_entropy:.3f}, yes={entropy_yes:.3f}, no={entropy_no:.3f}, gain={gain:.3f}")
    
    return max(0.0, gain)


def choose_next_question(graph: ProbabilityGraph, working_set: Set[str] = None) -> str | None:
    """
    Choose the next most informative symptom to ask about
    
    Args:
        graph: Probability graph
        working_set: Optional subset of nodes to consider (from FindPivots)
    
    Returns:
        ID of symptom with highest information gain, or None
    """
    # Filter to unknown symptoms
    candidates = [
        node_id for node_id, node in graph.nodes.items()
        if node["type"] == "symptom"
        and node.get("value") is None
        and (working_set is None or node_id in working_set)
    ]
    
    if not candidates:
        return None
    
    best_symptom = None
    best_gain = 0.0
    
    for symptom_id in candidates:
        gain = expected_information_gain(graph, symptom_id)
        if gain > best_gain:
            best_gain = gain
            best_symptom = symptom_id
    
    return best_symptom


def update_graph(
    graph: ProbabilityGraph,
    symptom_id: str,
    value: float
) -> ProbabilityGraph:
    """
    Update graph with new symptom value
    
    Args:
        graph: Probability graph
        symptom_id: ID of symptom to update
        value: New value (0-1 or specific score)
    
    Returns:
        Updated graph
    """
    if symptom_id in graph.nodes:
        graph.nodes[symptom_id]["value"] = value
    
    return graph


def propagate_update(
    graph: ProbabilityGraph,
    symptom_id: str
) -> ProbabilityGraph:
    """
    Propagate symptom update through graph (update disease probabilities)
    
    Args:
        graph: Probability graph
        symptom_id: ID of updated symptom
    
    Returns:
        Updated graph with propagated probabilities
    """
    symptom = graph.nodes.get(symptom_id)
    if not symptom or symptom.get("value") is None:
        return graph
    
    symptom_value = symptom["value"]
    
    # Find all edges from this symptom
    connected_edges = [e for e in graph.edges if e["from"] == symptom_id]
    
    for edge in connected_edges:
        target_id = edge["to"]
        target = graph.nodes.get(target_id)
        
        if not target or target["type"] != "disease":
            continue
        
        weight = edge.get("weight", 0.5)
        
        # Update probability based on symptom value and edge weight
        delta = weight * symptom_value
        current_prob = target.get("probability", 0.5)
        
        # Adjust probability (with bounds)
        new_prob = max(0.0, min(1.0, current_prob + delta - 0.5))
        graph.nodes[target_id]["probability"] = new_prob
    
    return graph


def get_total_entropy(graph: ProbabilityGraph) -> float:
    """
    Calculate total entropy across all disease nodes
    
    Args:
        graph: Probability graph
    
    Returns:
        Average entropy across diseases
    """
    disease_nodes = [
        node for node in graph.nodes.values()
        if node["type"] == "disease"
    ]
    
    if not disease_nodes:
        return 0.0
    
    total_entropy = sum(
        calculate_entropy(node.get("probability", 0.5))
        for node in disease_nodes
    )
    
    return total_entropy / len(disease_nodes)
