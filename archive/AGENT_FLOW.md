# Complete Urology Consultation Agent Flow

## 🎯 **The Secret Sauce: Small Context, Focused Agents**

Each agent has **ONE JOB** with a **SMALL CONTEXT** to work on. This allows efficient, clear progression through the consultation stages.

---

## **4-Agent Architecture**

```
User
  ↓
Host Agent → PI Agent → Graph Reasoning Agent → Recommendation Agent
  ↓             ↓               ↓                        ↓
Gather      Safety        Systematic             Final Action Plan
Story       Check         Questions              + Education
```

---

## **Agent 1: Host Agent**

**Job:** Gather the patient's story empathetically

**Tools:**
- `store_patient_info` - Age, gender, pregnancy
- `record_symptoms` - Symptom extraction
- `record_medical_history` - Medical background
- `record_patient_concerns` - What they're worried about, their thoughts, goals

**Context It Creates:**
```python
{
    "age": 45,
    "gender": "Male",
    "reported_symptoms": ["frequent urination", "weak stream"],
    "medical_history": ["diabetes"],
    "patient_concerns": ["worried about prostate cancer"],
    "patient_thoughts": "Maybe it's just getting older",
    "consultation_goals": ["understand PSA better", "avoid surgery if possible"]
}
```

**Handoff:** → PI Agent when story complete

---

## **Agent 2: PI Agent (Private Investigator)**

**Job:** Safety check + clinical context preparation

**Tools:**
- `check_safety_concerns` - Red flag detection
- `get_clinical_guidance` - Clinical context and pearls

**What It Does:**
1. Run safety check (silent if clear)
2. Get clinical context for the symptoms
3. Brief summary to patient
4. **IMMEDIATELY** hand off to Graph Reasoning Agent

**Context It Adds:**
```python
{
    "red_flags_checked": True,
    "red_flags_present": [],  # or ["testicular_torsion"] if emergency
    "safety_concerns": []
}
```

**Handoff:** → Graph Reasoning Agent

---

## **Agent 3: Graph Reasoning Agent**

**Job:** ONLY ask strategic questions to narrow diagnoses

**Tools:**
- `build_probability_graph` - Create reasoning graph
- `find_strategic_questions` - FindPivots algorithm
- `update_graph_with_answer` - Propagate probabilities

**What It Does:**
1. Build graph from all calculators (infection, pain, urology)
2. Find strategic questions using entropy/information gain
3. Ask ONE question at a time (SIQORSTAA format)
4. Update graph after each answer
5. Stop when entropy < 0.2 OR 10 questions asked
6. **Hand off to Recommendation Agent**

**Context It Adds:**
```python
{
    "probability_graph": {...},
    "current_entropy": 0.15,
    "questions_asked": 7,
    "calculated_differentials": {
        "uro_bph": 0.82,
        "uro_prostate_cancer": 0.15,
        "uro_uti": 0.03
    }
}
```

**Handoff:** → Recommendation Agent when done questioning

---

## **Agent 4: Recommendation Agent**

**Job:** Provide final recommendations, education, action plan

**Tools:**
- `get_patient_education` - Educational content (e.g., PSA explanations)
- `generate_patient_action_plan` - Comprehensive action plan
- `generate_gp_referral_letter` - Formal GP letter

**What It Does:**
1. Review all context (concerns, goals, differentials)
2. Address patient concerns with education
3. Generate comprehensive action plan
4. Present recommendations
5. Offer GP letter

**Example Output:**
```markdown
# Patient Action Plan

**Patient Information:**
- Age: 45
- Gender: Male
- Chief Complaint: Frequent urination and weak stream

**Patient Concerns:**
You mentioned you were worried about prostate cancer. Let me address that directly:

[Uses get_patient_education("PSA") to explain]

**Differential Diagnosis:**
1. Benign Prostatic Hyperplasia (BPH) - 82% probability
2. Prostate Cancer - 15% probability
3. UTI - 3% probability

**Recommended Investigations:**
- PSA blood test
- Urine dipstick
- Digital rectal exam
- Post-void residual measurement

**Management Plan:**
For BPH, you mentioned wanting to avoid surgery. Good news - 60-80% of men improve with medications alone:
- Alpha-blockers (e.g., Tamsulosin) - work within days
- 5-Alpha Reductase Inhibitors - shrink prostate over 6-12 months
- Surgery only if medications fail

**Next Steps:**
1. Get PSA and urine test at GP
2. Start lifestyle modifications (reduce caffeine, etc.)
3. If PSA elevated, check for infection first
4. Follow up after investigations

Would you like me to generate a summary letter for your GP?
```

**No Handoff:** This is the final agent

---

## **Complete Flow Example: Urology Case**

### **User:** "I'm having trouble urinating"

### **Host Agent:**
- "Tell me more about what's been bothering you..."
- Records: frequent urination, weak stream, nocturia
- "How old are you?" → 45, Male
- "Is there anything specific you're worried about?" → "Prostate cancer"
- "What are you hoping to get from this?" → "Understand my options, avoid surgery"
- **→ Hands off to PI**

### **PI Agent:**
- Runs `check_safety_concerns` → No red flags
- Gets `clinical_guidance` for urinary symptoms
- "Based on what you've shared, I need to ask some specific questions..."
- **→ Hands off to Graph Reasoning**

### **Graph Reasoning Agent:**
- Builds graph: UTI, BPH, prostate cancer, overactive bladder nodes
- FindPivots identifies: "weak_stream" (high info gain)
- Q1: "On a scale of 0-10, how weak is your urine stream?"
  - A1: "7" → Updates graph, BPH probability ↑
- Q2: "Do you have to strain to start urinating?"
  - A2: "Yes" → BPH probability ↑↑
- Q3: "Any pain or burning when urinating?"
  - A3: "No" → UTI probability ↓
- Entropy drops to 0.18 after 7 questions
- "Thank you, I have enough information now..."
- **→ Hands off to Recommendation**

### **Recommendation Agent:**
- Reviews: Concern = "prostate cancer", Goal = "avoid surgery"
- Uses `get_patient_education("psa_normal_doesnt_rule_out_cancer")`
- Uses `generate_patient_action_plan`
- Presents comprehensive plan addressing concerns
- Explains BPH medications vs surgery
- Offers GP letter

---

## **Why This Works:**

### **✅ Small Context Per Agent:**
- Host: Just gathering story
- PI: Just safety + prep
- Graph: Just questioning
- Recommendation: Just final output

### **✅ Clear Handoffs:**
Each agent knows exactly when to stop and pass to next

### **✅ Focused Tools:**
No agent has "swiss army knife" of tools - only what it needs

### **✅ Scalable:**
Easy to add more specialties (cardiac, respiratory) - just add calculators to graph

---

## **File Structure:**

```
differentials/
├── graph_engine.py              # FindPivots, entropy, propagation
├── graph_builder.py             # Build graphs from calculators
├── urology_conditions.py        # 14 urological conditions ✅
├── pain_conditions.py           # Pain differential matrix
├── clinical_education.py        # Patient education content ✅
├── letter_generator.py          # Action plans + GP letters ✅
└── differentialCalculations.jsx # JS infection calculators

main.py                          # 4 agents defined
tools.py                         # All function tools
api.py                           # FastAPI endpoints
```

---

## **Next Steps to Test:**

1. Start backend:
   ```bash
   python -m uvicorn api:app --reload
   ```

2. Test conversation:
   - "Hello"
   - "I have trouble urinating, weak stream"
   - Answer Host's questions (age, concerns, goals)
   - Watch PI do safety check
   - Answer Graph's strategic questions
   - Receive comprehensive action plan

3. Verify handoffs happen automatically at right times

---

**This is the complete urology pathway with maximum output!** 🎉
