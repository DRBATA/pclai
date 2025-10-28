# Urology Calculator - Quick Start Guide

## Run the Tests

```bash
cd python-backend
python test_urology_calculator.py
```

**Expected Output:**
```
================================================================================
UROLOGY BAYESIAN CALCULATOR - TEST SUITE
================================================================================

================================================================================
TEST CASE 1: Young Woman with Acute UTI Symptoms
================================================================================

Patient: 28-year-old female
Symptoms: ['pain_burning', 'urgency']
Onset: sudden (dysuria severity 75/100)

--- PROBABILITIES ---
  uti                       92.5%
  overactive_bladder         4.2%
  interstitial_cystitis      2.1%
  prostatitis                0.8%
  kidney_stones              0.2%
  prostate_cancer            0.1%
  bph                        0.1%

Entropy: 0.421

--- RECOMMENDATION ---
  Primary: Likely urinary tract infection
  Confidence: high
  Action: See GP this week for urine test and antibiotics
  Urgency: routine

...
```

---

## Test Cases Explained

### **Case 1: Young Woman with Acute UTI** ✅
- **Age:** 28, Female
- **Symptoms:** Sudden onset (yesterday), dysuria 75/100, urgency
- **Expected:** UTI ~92% (high confidence)
- **Key Factors:** Sudden onset (+5), dysuria (+1.5), female baseline (30%)

### **Case 2: Elderly Man with BPH** ✅
- **Age:** 72, Male
- **Symptoms:** Gradual onset (5 years), weak stream 85/100, nocturia 4x/night
- **Expected:** BPH ~85% (high confidence)
- **Key Factors:** Gradual onset (+5), weak stream (+4), age 70+ prior (85%)

### **Case 3: Man with Kidney Stones** ✅
- **Age:** 45, Male
- **Symptoms:** Sudden onset (2 hours), pain 95/100, hematuria, history of stones
- **Expected:** Kidney stones ~88% (very high confidence)
- **Key Factors:** Sudden onset (+5), severe pain (+7), hematuria (+6), prior stones (50%)

### **Case 4: Man with Prostatitis** ✅
- **Age:** 52, Male
- **Symptoms:** Sudden onset, dysuria 70/100, **FEVER**, pelvic pain
- **Expected:** Prostatitis ~70%, UTI ~15%, BPH ~1%
- **Key Factors:** Fever (+7 for prostatitis, **-8 for BPH**), sudden onset (+2)

### **Case 5: Uncertain Case** ⚠️
- **Age:** 55, Male
- **Symptoms:** Only urgency + frequency (minimal info)
- **Expected:** Multiple possibilities, high entropy
- **Key Factors:** Needs more questions to narrow down

---

## How to Use the Calculator

### **Basic Usage:**

```python
from differentials.urology_calculator import compute_urology_differential, calculate_entropy

# Define patient
patient_info = {
    "age": 62,
    "gender": "male",
    "family_history_prostate_cancer": False,
    "previous_kidney_stones": False
}

# Define symptoms
symptoms = {
    "onset_speed": "gradual",
    "weak_stream_severity": 70,
    "nocturia_per_night": 3,
    "reported_symptoms": ["weak_stream", "nocturia"],
    "fever_present": False
}

# Calculate
result = compute_urology_differential(symptoms, patient_info)

# Get probabilities
probs = result["probabilities"]
print(f"BPH: {probs['bph']:.1%}")
print(f"UTI: {probs['uti']:.1%}")

# Get entropy
entropy = calculate_entropy(probs)
print(f"Entropy: {entropy:.3f}")

# Get recommendation
rec = result["recommendation"]
print(f"Action: {rec['action']}")
```

---

## Symptom Input Format

### **Discrete Symptoms:**
```python
symptoms = {
    "onset_speed": "sudden" or "gradual",
    "fever_present": True or False,
    "dysuria": True or False,
    "hematuria": True or False,
    "reported_symptoms": ["pain_burning", "urgency", "weak_stream", ...],
}
```

### **Continuous Symptoms (0-100 scale):**
```python
symptoms = {
    "dysuria_severity": 0-100,      # Pain intensity
    "weak_stream_severity": 0-100,  # How weak (0=normal, 100=always weak)
    "pain_severity": 0-100,         # General pain intensity
    "nocturia_per_night": 0-10,     # Number of times waking
}
```

### **Risk Factors:**
```python
patient_info = {
    "age": 50,
    "gender": "male" or "female",
    "family_history_prostate_cancer": True or False,
    "previous_kidney_stones": True or False,
}
```

---

## Output Format

### **Probabilities:**
```python
result["probabilities"] = {
    "uti": 0.45,
    "bph": 0.32,
    "kidney_stones": 0.15,
    "overactive_bladder": 0.05,
    "prostatitis": 0.02,
    "interstitial_cystitis": 0.01,
    "prostate_cancer": 0.00
}
```

### **Recommendation:**
```python
result["recommendation"] = {
    "primary_diagnosis": "Likely urinary tract infection",
    "confidence": "high",
    "action": "See GP this week for urine test and antibiotics",
    "self_care": ["Drink plenty of water", ...],
    "red_flags": "See GP urgently if fever develops...",
    "urgency": "routine",
    "probability": 0.92
}
```

### **Graph Structure (for FindPivots):**
```python
result["graph"] = {
    "nodes": {
        "uro_uti": {"type": "disease", "probability": 0.45, "label": "Uti"},
        "weak_stream": {"type": "symptom", "value": 1.0, "label": "Weak Stream"},
        ...
    },
    "edges": [
        {"from": "weak_stream", "to": "uro_bph", "weight": 0.95},
        ...
    ]
}
```

### **Entropy:**
```python
entropy = calculate_entropy(result["probabilities"])
# Returns: 0.0 (certain) to ~2.8 (very uncertain)
# Stop questioning when entropy < 0.05
```

---

## Integration with Graph Agent

### **Step 1: Build Graph**
```python
# Graph Agent calls this
result = build_probability_graph(context)
# Returns: probabilities, graph, entropy, recommendation
```

### **Step 2: Find Strategic Questions**
```python
# Graph Agent calls this
questions = find_strategic_questions(context)
# Returns: top 1-3 questions ranked by information gain
```

### **Step 3: Update with Answer**
```python
# After PI Agent gets patient answer
updated = update_graph_with_answer(context, symptom_id, value)
# Returns: new probabilities, new entropy
```

### **Step 4: Loop Until Done**
```python
while entropy > 0.05:
    questions = find_strategic_questions(context)
    # PI Agent asks best question
    # Patient answers
    updated = update_graph_with_answer(context, symptom_id, value)
    entropy = updated["new_entropy"]

# Done! Make recommendation
recommendation = context.recommendation
```

---

## Key Thresholds

| Metric | Value | Meaning |
|--------|-------|---------|
| **Entropy** | < 0.05 | Stop questioning, make recommendation |
| **Confidence** | > 0.65 | High confidence in diagnosis |
| **Top Probability** | > 0.50 | Clear leader |
| **Entropy** | 0.5-1.0 | Moderate uncertainty |
| **Entropy** | > 1.5 | High uncertainty, need more questions |

---

## Evidence Sources

All priors and symptom weights are based on:

- ✅ **Epidemiology:** EPIC, NOBLE, SEER, Cancer Research UK
- ✅ **Diagnostic Studies:** Bent et al JAMA 2002 (dysuria), Berry et al (BPH)
- ✅ **Clinical Guidelines:** EAU 2023-2025, NICE NG131, AUA
- ✅ **Nephrology:** Stone hematuria prevalence (85%)
- ✅ **Oncology:** Bladder cancer hematuria (85%)

See `uro_weights.md` for full research details.

---

## Troubleshooting

### **Entropy not decreasing?**
- Check that symptoms are being updated in context
- Verify `update_graph_with_answer()` is called after each answer
- Make sure new symptoms have non-zero SYMPTOM_POINTS

### **Probabilities seem wrong?**
- Check patient_info (age, gender matter!)
- Verify symptom values are in correct range (0-100 for continuous)
- Look at log_odds in output to debug

### **Questions repeating?**
- Check that `checked` set is tracking asked symptoms
- Verify FindPivots is excluding known symptoms

---

## Next Steps

1. ✅ Run `test_urology_calculator.py` to verify setup
2. ✅ Integrate with Graph Agent in `tools.py`
3. ✅ Test with real patient cases
4. ✅ Calibrate thresholds based on performance
5. ✅ Deploy to production

---

**Ready to test?** Run:
```bash
python test_urology_calculator.py
```

**Questions?** Check `RESEARCH_INTEGRATION_COMPLETE.md` for detailed explanation of all values.
