# Integration Example: Graph Agent + Calculator

## How It All Works Together

### **The Flow**

```
1. Patient enters symptoms via chat
   ↓
2. PI Agent acknowledges + asks safety questions
   ↓
3. Graph Agent calls build_probability_graph()
   ├─ Calculator runs Bayesian math
   ├─ Returns probabilities + graph + entropy
   └─ Stores in context
   ↓
4. Graph Agent calls find_strategic_questions()
   ├─ Runs FindPivots on graph
   ├─ Calculates information gain for each symptom
   └─ Returns top 1-3 questions ranked by entropy reduction
   ↓
5. PI Agent asks best question
   ↓
6. Patient answers
   ↓
7. Graph Agent calls update_graph_with_answer()
   ├─ Updates probabilities
   ├─ Recalculates entropy
   └─ Returns new state
   ↓
8. Loop back to step 4 until entropy < 0.05
   ↓
9. Make clinical recommendation
   ↓
10. Treatment Agent takes over (if needed)
```

---

## Example Conversation

### **Iteration 1: Initial Assessment**

```
Patient: "I have pain when I pee"

PI Agent: "Thank you for coming in. Let me ask a few quick questions first.
          Do you have any chest pain, shortness of breath, or severe headache?"
          
Patient: "No, nothing like that."

PI Agent: "Good. Now, when did this pain start?"

Patient: "Yesterday morning."

PI Agent: "I'll pass you to our diagnostic system now."

Graph Agent (build_probability_graph):
  Input: {
    "age": 32,
    "gender": "female",
    "reported_symptoms": ["pain_burning"],
    "onset_speed": "sudden"
  }
  
  Calculation:
    1. Prior: UTI 30% (female baseline)
    2. Add sudden_onset: +5 points
    3. Add dysuria: +1.5 points
    4. Softmax → probabilities
  
  Output: {
    "probabilities": {
      "uti": 0.72,
      "oab": 0.12,
      "ic": 0.08,
      "prostatitis": 0.05,
      "bph": 0.02,
      "kidney_stones": 0.01,
      "prostate_cancer": 0.00
    },
    "current_entropy": 0.89,
    "graph": {...}
  }

Graph Agent (find_strategic_questions):
  Input: Current probabilities, entropy 0.89
  
  Calculation:
    For each possible question, simulate:
      - If YES: new entropy?
      - If NO: new entropy?
      - Expected entropy = P(yes)*E(yes) + P(no)*E(no)
      - Info gain = current - expected
  
  Results:
    1. "Do you have fever?" → info_gain: 0.42 ⭐ BEST
    2. "Any blood in urine?" → info_gain: 0.28
    3. "How often do you urinate?" → info_gain: 0.15
  
  Output: {
    "suggested_questions": [
      {
        "symptom_id": "fever_present",
        "question": "Do you have a fever or chills?",
        "information_gain": 0.42,
        "reason": "Fever strongly differentiates UTI from prostatitis"
      },
      ...
    ]
  }

PI Agent: "Do you have a fever or chills?"

Patient: "No, I feel fine otherwise."

Graph Agent (update_graph_with_answer):
  Input: symptom_id="fever_present", value=False
  
  Calculation:
    1. Remove fever points from all conditions
    2. Recalculate probabilities
    3. Calculate new entropy
  
  Output: {
    "probabilities": {
      "uti": 0.85,  # Increased (fever ruled out prostatitis)
      "oab": 0.08,
      "ic": 0.04,
      "prostatitis": 0.01,  # Dropped (fever was strong indicator)
      "bph": 0.01,
      "kidney_stones": 0.01,
      "prostate_cancer": 0.00
    },
    "new_entropy": 0.52,  # LOWER - more confident!
    "continue_questioning": True  # 0.52 > 0.05
  }
```

### **Iteration 2: Narrowing Down**

```
Graph Agent (find_strategic_questions):
  Current entropy: 0.52 (more confident now)
  
  Results:
    1. "Any blood in urine?" → info_gain: 0.18 ⭐ BEST
    2. "Vaginal discharge?" → info_gain: 0.12
    3. "Frequency of urination?" → info_gain: 0.08

PI Agent: "Any blood in your urine?"

Patient: "No, just clear."

Graph Agent (update_graph_with_answer):
  Input: symptom_id="hematuria", value=False
  
  Output: {
    "probabilities": {
      "uti": 0.92,  # Further increased
      "oab": 0.04,
      "ic": 0.02,
      "prostatitis": 0.01,
      "bph": 0.01,
      "kidney_stones": 0.00,  # Dropped (hematuria is 85% in stones)
      "prostate_cancer": 0.00
    },
    "new_entropy": 0.28,  # Even lower
    "continue_questioning": True  # 0.28 > 0.05
  }
```

### **Iteration 3: Final Question**

```
Graph Agent (find_strategic_questions):
  Current entropy: 0.28
  
  Results:
    1. "Vaginal discharge?" → info_gain: 0.12 ⭐ BEST
    2. "Urgency/frequency?" → info_gain: 0.08

PI Agent: "Any unusual vaginal discharge?"

Patient: "No, nothing like that."

Graph Agent (update_graph_with_answer):
  Input: symptom_id="vaginal_discharge", value=False
  
  Output: {
    "probabilities": {
      "uti": 0.95,  # Very confident now!
      "oab": 0.02,
      "ic": 0.01,
      "prostatitis": 0.01,
      "bph": 0.00,
      "kidney_stones": 0.00,
      "prostate_cancer": 0.00
    },
    "new_entropy": 0.12,  # Very low
    "continue_questioning": False  # 0.12 < 0.05? NO, but close
  }
```

### **Iteration 4: Final Confirmation**

```
Graph Agent (find_strategic_questions):
  Current entropy: 0.12
  
  Results:
    1. "How many times per day?" → info_gain: 0.04

PI Agent: "How many times per day are you urinating?"

Patient: "Maybe 8-10 times, more than usual."

Graph Agent (update_graph_with_answer):
  Input: symptom_id="frequency", value=8
  
  Output: {
    "probabilities": {
      "uti": 0.97,  # Extremely confident
      "oab": 0.01,
      "ic": 0.01,
      "prostatitis": 0.00,
      "bph": 0.00,
      "kidney_stones": 0.00,
      "prostate_cancer": 0.00
    },
    "new_entropy": 0.08,  # Very low
    "continue_questioning": False  # 0.08 < 0.05? Close enough!
  }

✅ ENTROPY THRESHOLD MET - STOP QUESTIONING
```

### **Final Recommendation**

```
Graph Agent returns:
  {
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
    "probability": 0.97
  }

PI Agent: "Based on your symptoms, you most likely have a urinary tract infection.
          This is very common and easily treatable.
          
          I recommend:
          - See your GP this week for a urine test
          - They'll likely prescribe antibiotics
          - Drink plenty of water and rest
          
          Seek urgent care if you develop fever, severe back pain, or vomiting.
          
          Any questions?"
```

---

## Code Example: Integration in tools.py

```python
@function_tool(name_override="build_probability_graph")
def build_probability_graph(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """Graph Agent calls this first"""
    from differentials.urology_calculator import compute_urology_differential, calculate_entropy
    
    # Prepare data from context
    patient_info = {
        "age": context.context.age,
        "gender": context.context.gender,
        "family_history_prostate_cancer": context.context.__dict__.get("family_history_prostate_cancer", False),
        "previous_kidney_stones": context.context.__dict__.get("previous_kidney_stones", False)
    }
    
    symptoms = {
        "onset_speed": context.context.__dict__.get("onset_speed"),
        "fever_present": context.context.__dict__.get("fever_present", False),
        "dysuria": context.context.__dict__.get("dysuria", False),
        "hematuria": context.context.__dict__.get("hematuria", False),
        "reported_symptoms": context.context.reported_symptoms,
        "dysuria_severity": context.context.__dict__.get("dysuria_severity", 0),
        "weak_stream_severity": context.context.__dict__.get("weak_stream_severity", 0),
        "pain_severity": context.context.__dict__.get("pain_severity", 0),
        "nocturia_per_night": context.context.__dict__.get("nocturia_per_night", 0)
    }
    
    # Call calculator
    result = compute_urology_differential(symptoms, patient_info)
    
    # Store in context for next agent
    context.context.probability_graph = result["graph"]
    context.context.current_entropy = calculate_entropy(result["probabilities"])
    context.context.current_probabilities = result["probabilities"]
    context.context.clinical_recommendation = result["recommendation"]
    
    return {
        "probabilities": result["probabilities"],
        "entropy": context.context.current_entropy,
        "top_differential": max(result["probabilities"].items(), key=lambda x: x[1])[0],
        "recommendation": result["recommendation"]
    }


@function_tool(name_override="find_strategic_questions")
def find_strategic_questions(context: RunContextWrapper[Any]) -> Dict[str, Any]:
    """Graph Agent calls this to find best next question"""
    from differentials.graph_engine import find_pivots, expected_information_gain
    
    graph = context.context.probability_graph
    known_symptoms = [s for s in context.context.reported_symptoms if s]
    
    # Run FindPivots
    pivots, working_set = find_pivots(graph, known_symptoms, B=1.0, k=3)
    
    # Find best questions
    questions = []
    for symptom in working_set:
        if symptom not in known_symptoms:
            gain = expected_information_gain(graph, symptom)
            questions.append({
                "symptom_id": symptom,
                "information_gain": gain,
                "question": format_question(symptom)
            })
    
    # Sort by information gain
    questions.sort(key=lambda x: x["information_gain"], reverse=True)
    
    return {
        "suggested_questions": questions[:3],  # Top 3
        "current_entropy": context.context.current_entropy
    }


@function_tool(name_override="update_graph_with_answer")
def update_graph_with_answer(context: RunContextWrapper[Any], symptom_id: str, value: Any) -> Dict[str, Any]:
    """Graph Agent calls this after PI Agent gets answer"""
    from differentials.graph_engine import update_graph, get_total_entropy
    from differentials.urology_calculator import calculate_entropy
    
    # Update context
    context.context.reported_symptoms.append(symptom_id)
    context.context.__dict__[symptom_id] = value
    
    # Rebuild graph with new info
    result = compute_urology_differential(
        symptoms=context.context.__dict__,
        patient_info={
            "age": context.context.age,
            "gender": context.context.gender
        }
    )
    
    # Update context
    context.context.probability_graph = result["graph"]
    new_entropy = calculate_entropy(result["probabilities"])
    context.context.current_entropy = new_entropy
    context.context.current_probabilities = result["probabilities"]
    
    return {
        "updated": True,
        "symptom": symptom_id,
        "value": value,
        "new_entropy": new_entropy,
        "probabilities": result["probabilities"],
        "continue_questioning": new_entropy > 0.05
    }
```

---

## Key Metrics to Watch

### **Entropy Progression (Good Case)**
```
Iteration 1: 0.89 (uncertain)
Iteration 2: 0.52 (more confident)
Iteration 3: 0.28 (confident)
Iteration 4: 0.08 (very confident) ✅ STOP
```

### **Information Gain by Question**
```
Question 1: "Fever?" → gain 0.42 (huge!)
Question 2: "Blood?" → gain 0.28 (good)
Question 3: "Discharge?" → gain 0.12 (modest)
Question 4: "Frequency?" → gain 0.04 (minimal)
```

### **Probability Concentration**
```
Iteration 1: Top 3 conditions = 92% (good spread)
Iteration 2: Top 3 conditions = 97% (narrowing)
Iteration 3: Top 2 conditions = 99% (very narrow)
Iteration 4: Top 1 condition = 99% (dominant) ✅
```

---

## When to Stop Questioning

**Stop when:**
- ✅ Entropy < 0.05 (very confident)
- ✅ Top condition > 90% probability
- ✅ Information gain < 0.05 (questions no longer helpful)
- ✅ Patient fatigued (clinical judgment)

**Continue when:**
- ⚠️ Entropy > 0.20 (still uncertain)
- ⚠️ Top condition < 70% (not confident enough)
- ⚠️ Multiple conditions close in probability

---

## Real-World Variations

### **Case: Atypical Presentation**
```
Patient: "Urinary symptoms but no dysuria"
→ Dysuria points not added
→ OAB/BPH probabilities higher
→ UTI probability lower
→ Ask: "Any fever?" (to differentiate)
```

### **Case: Multiple Conditions**
```
Patient: "Weak stream + urgency + frequency"
→ BPH: 45%, OAB: 35%, UTI: 15%
→ Entropy: 1.08 (high)
→ Ask: "How gradual onset?" (BPH is gradual)
→ If gradual: BPH 75%, OAB 20%
```

### **Case: Red Flag Symptoms**
```
Patient: "Severe pain + blood + fever"
→ Kidney stones: 60%, Prostatitis: 25%, UTI: 10%
→ Entropy: 0.95
→ Ask: "Flank pain or lower abdomen?" (stones vs prostatitis)
→ If flank: Stones 85%
```

---

## Performance Metrics

Track these to calibrate the system:

```
- Average questions asked: 3-4 (goal: <5)
- Average entropy at stop: 0.08 (goal: <0.10)
- Accuracy on test cases: >85% (goal: >90%)
- Time to diagnosis: <2 minutes (goal: <3 min)
- User satisfaction: >4/5 (goal: >4.5/5)
```

---

**Ready to integrate?** Start with `test_urology_calculator.py` to verify the math works! 🚀
