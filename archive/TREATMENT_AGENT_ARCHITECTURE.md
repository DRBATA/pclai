# Treatment Agent Architecture

## Overview

Converted surgical intake form into modular backend calculators with tool interfaces for the Treatment Agent.

---

## What Was Built

###  1. **Backend Calculators** (`procedural/procedural_calculators.py`)

Evidence-based calculators that replace the React form logic:

#### **MRI Fusion Biopsy Indicator**
```python
calculate_mri_fusion_indication(pirads, psad, psa_velocity, lesion_size_mm)
→ Returns: band (strong/consider/weak), evidence citations, urgency
```

**Evidence base:**
- EAU 2025 PI-RADS
- NICE NG131-2024
- Carter JAMA 2021
- Radiology 2020

#### **HIFU Eligibility Calculator**
```python
calculate_hifu_eligibility(pirads, lesion_size_mm, gleason, prostate_volume)
→ Returns: eligibility band, contraindications, cost (£16k), window notes
```

**Evidence base:**
- EAU 2023
- Ahmed 2021 Lancet Oncology

#### **AS vs Surgery Utility Comparison**
```python
calculate_active_surveillance_vs_surgery(age, psad, pirads, gleason, comorbidity, preferences)
→ Returns: relative scores, margin, preference (equipoise/AS/surgery)
```

**Non-prescriptive:** Decision support, not directive!

#### **Treatment Plan Generator**
```python
generate_treatment_summary(patient_data, mri_result, hifu_result, as_vs_surgery)
→ Returns: Complete plan with pathways, booking recommendations, emails
```

---

### 2. **Agent Tools** (`tools.py`)

Four new tools for the Treatment Agent:

#### **assess_biopsy_indication**
```python
@function_tool
def assess_biopsy_indication(context, pirads, psad, psa_velocity, lesion_size_mm)
```

Agent calls this after collecting PSA/MRI data.

#### **assess_hifu_eligibility**
```python
@function_tool
def assess_hifu_eligibility(context, pirads, lesion_size_mm, gleason, prostate_volume)
```

Agent calls this to check HIFU suitability.

#### **compare_treatment_options**
```python
@function_tool
def compare_treatment_options(
    context, age, psad, pirads, gleason, comorbidity,
    urinary_concern, sexual_concern, avoid_overtreatment
)
```

Agent calls this after understanding patient preferences.

#### **generate_treatment_plan**
```python
@function_tool
def generate_treatment_plan(context)
```

Final call - generates complete plan with emails.

---

## Treatment Agent Conversation Flow

```
1. User: "I've been told I might need a prostate biopsy"

2. Treatment Agent:
   - Asks about PSA, MRI results (PI-RADS), lesion size
   - Collects: PSA, prostate volume, PI-RADS, lesion size

3. Agent calls: assess_biopsy_indication(pirads=4, psad=0.18, lesion_size_mm=12)
   ↓
   Returns: {
     "band": "strong",
     "recommendation": "MRI fusion biopsy strongly indicated",
     "matched_criteria": [
       {"label": "PI-RADS ≥4", "evidence": "EAU-2025-PI-RADS"},
       {"label": "PSAD ≥0.15", "evidence": "NICE-NG131-2024"},
       {"label": "Lesion ≥8 mm", "evidence": "Radiology-2020-Mehralivand"}
     ],
     "urgency": "routine"
   }

4. Agent:
   "Based on your results, an MRI fusion biopsy is strongly recommended:
   - Your PI-RADS score of 4 suggests significant abnormality (EAU 2025)
   - Your PSA density of 0.18 is above the threshold (NICE guidelines)
   - Lesion size of 12mm is ideal for targeting
   
   This is a routine procedure, not urgent. Would you like to discuss what it involves?"

5. User: "Yes, and what are my options if it shows cancer?"

6. Agent:
   - Asks about concerns: urinary function? sexual function? overtreatment?
   - Collects preferences

7. Agent calls: compare_treatment_options(
     age=62, psad=0.18, pirads=4, gleason="3+4", comorbidity="low",
     urinary_concern=0.7, sexual_concern=0.8, avoid_overtreatment=0.6
   )
   ↓
   Returns: {
     "preference": "equipoise",
     "scores": {"active_surveillance": 0.65, "surgery_rp": 0.62},
     "margin": 0.03,
     "note": "Scores very close - excellent candidate for shared decision making"
   }

8. Agent:
   "Good news - you're in a situation where both Active Surveillance and Surgery are reasonable options:
   
   - Active Surveillance score: 0.65
   - Surgery score: 0.62
   - These are very close (margin: 0.03)
   
   This means you have time to consider what matters most to you. Given your concerns about urinary and sexual function, Active Surveillance might appeal, but surgery offers definitive treatment.
   
   Would you like to explore HIFU as a middle-ground option?"

9. Agent calls: assess_hifu_eligibility(pirads=4, lesion_size_mm=12, gleason="3+4", prostate_volume=45)
   ↓
   Returns: {
     "band": "strong",
     "recommendation": "HIFU focal therapy may be suitable",
     "window_note": "Lesion size in ideal focal window (8–15 mm)",
     "estimated_cost_gbp": 16000,
     "site_block": "HIFU not available at this site - would require referral"
   }

10. Agent:
    "HIFU focal therapy could be an excellent option for you:
    
    ✅ Your lesion is 12mm - ideal size for focal treatment
    ✅ Gleason 3+4 is suitable
    ✅ Prostate volume (45cc) is within range
    
    ⚠️ HIFU isn't available at our main site - you'd need referral to [specialist centre]
    💷 Private cost: approximately £16,000
    
    HIFU targets just the cancer, potentially preserving more function than full surgery, but with slightly less certainty of cancer clearance.
    
    Would you like me to summarize all your options?"

11. Agent calls: generate_treatment_plan(context)
    ↓
    Returns: {
      "summary": {
        "pathways": [
          {"name": "MRI Fusion Biopsy", "priority": "high", "next_steps": [...]},
          {"name": "HIFU Focal Therapy", "cost_estimate_gbp": 16000, ...},
          {"name": "Active Surveillance", ...}
        ],
        "booking": {
          "suggested_timing": "within_6_weeks",
          "theatre_priority": "standard",
          "patient_readiness": "needs_discussion"
        }
      },
      "patient_email_content": "[Full email text]",
      "clinical_summary": "[EMR summary]"
    }

12. Agent:
    "I've prepared a comprehensive summary for you. Here are your options:
    
    **1. MRI Fusion Biopsy** (Recommended first step)
       - What: Targeted biopsy guided by your MRI
       - When: Within 6 weeks (routine, not urgent)
       - Next: Results in 2-3 weeks, then discuss treatment
    
    **2. If Biopsy Confirms Cancer:**
       
       **Option A: Active Surveillance**
       - Regular monitoring with PSA tests and repeat MRI
       - Good fit given your concerns about side effects
       - Can always escalate to treatment if needed
       
       **Option B: HIFU Focal Therapy** ⭐
       - Treats just the cancer area
       - Better preservation of urinary/sexual function
       - Requires referral to specialist centre
       - Cost: £16,000 (private)
       
       **Option C: Surgery (Radical Prostatectomy)**
       - Definitive treatment, removes entire prostate
       - Higher certainty of cancer clearance
       - More impact on urinary/sexual function
       - NHS-funded (or private if preferred)
    
    **My Recommendation:**
    Start with the MRI fusion biopsy, then we can make a more informed decision. Given your preference profile and lesion characteristics, HIFU looks promising but let's see biopsy results first.
    
    **Next Steps:**
    1. I'll email you a detailed summary
    2. Would you like to book the biopsy?
    3. Any questions about the procedures or options?"

13. User: "Yes, let's book the biopsy"

14. Agent:
    "Perfect! I'm sending you:
    
    📧 **Patient Email** - Summary of our discussion + information leaflets
    📋 **Booking Form** - Choose your preferred date
    🏥 **Clinical Summary** - For your GP/urologist (de-identified)
    
    The email includes:
    - What to expect during biopsy
    - How to prepare
    - When to get results
    - All your options explained
    - Contact details for questions
    
    Anything else I can help with?"
```

---

## Email Outputs

### **Patient Email** (Generated by `_generate_patient_email()`)

```
Dear [Patient],

Thank you for discussing your prostate health with us. Based on our conversation, here's what we recommend:

1. MRI Fusion Biopsy
   Why: Based on your PSA levels, MRI findings, and personal preferences
   Next steps: Book biopsy appointment, Discuss anticoagulant management if applicable
   Timing: Routine

2. HIFU Focal Therapy
   Why: Your lesion size and Gleason score make you a good candidate
   Next steps: Specialist urology consultation required, Discuss procedure risks and benefits
   Timing: Elective
   
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
```

### **Clinical Summary** (Generated by `_generate_clinical_summary()`)

```
CLINICAL DECISION SUPPORT SUMMARY

Patient Profile:
- Age: 62
- PSA: 8.2 ng/mL
- PSA Density: 0.18
- PI-RADS: 4
- Gleason: 3+4
- Comorbidity: low

MRI Fusion Biopsy Indication: STRONG
- Score: 2.87
- Evidence: EAU-2025-PI-RADS, NICE-NG131-2024, Radiology-2020-Mehralivand

HIFU Eligibility: STRONG
- Score: 2.45
- Contraindications: None identified

Recommended Pathways:
- MRI Fusion Biopsy (high priority)
- HIFU Focal Therapy (medium priority)
- Active Surveillance (medium priority)

Decision Support Algorithm Version: 2.0
Evidence Base: EAU 2023-2025, NICE NG131-2024, Ahmed 2021

Note: This is decision support output. Clinical judgment and MDT review required.
```

---

## Theatre Booking Intelligence

The system helps manage capacity:

### **Priority Levels:**
```python
_determine_theatre_priority():
  - "priority" → Gleason 4+3/≥8, urgent cases
  - "standard" → Typical cases, age <65
  - "flexible" → Lower urgency, can accommodate schedule
```

### **Timing Recommendations:**
```python
_determine_booking_timing():
  - "within_2_weeks" → Urgent pathways
  - "within_6_weeks" → Routine (most biopsies)
  - "elective_3_6_months" → Non-urgent (AS follow-ups)
```

### **Patient Readiness:**
```python
_assess_patient_readiness():
  - "ready_to_book" → All concerns addressed, clear pathway
  - "needs_discussion" → High anxiety, site constraints, unclear pathway
  
  Returns concerns list for nurse specialist review
```

**Prevents overbooking:** If theatre has 6 slots, system flags "flexible" cases that can be rescheduled if urgent cases arrive.

---

## Integration Points

### **With Fly Email Agent:**

```python
# After generate_treatment_plan()
treatment_plan = context.context.treatment_plan

# Send via your email agent
fly_email_agent.send(
    to=patient_email,
    subject="Your Prostate Health Discussion Summary",
    body=treatment_plan["patient_email_content"],
    hash_code=generate_hash(patient_data)  # De-identified
)

# Send clinical summary to EMR
emr.store(treatment_plan["clinical_summary"])
```

### **With LiveKit (Optional):**

Not required for text-based consultations!

Use LiveKit only if you want:
- Video consultations
- Voice-based explanations
- Screen sharing of MRI images

Text chat via API is sufficient for this workflow.

---

## Data Privacy

### **Patient Email:**
- Contains: Recommendations, next steps, general education
- NO raw clinical data (PSA values, Gleason scores)
- Safe to send via regular email

### **Clinical Summary:**
- Contains: Full clinical data + algorithm outputs
- Stored in secure EMR only
- Includes hash code for linking without PII

### **De-identification:**
```python
hash_code = hashlib.sha256(f"{patient_id}_{timestamp}".encode()).hexdigest()[:12]
# e.g., "a3f7d2c9b1e8"

# Patient email footer:
"Reference: a3f7d2c9b1e8"

# Clinical system can look up by hash without exposing patient ID
```

---

## Next Steps

1. **Create Treatment Agent** in `main.py`:
   ```python
   treatment_agent = Agent(
       name="treatment_agent",
       model="gpt-4o",
       instructions="""
       You are a treatment pathway specialist...
       Use assess_biopsy_indication, assess_hifu_eligibility, compare_treatment_options,
       and generate_treatment_plan to create evidence-based recommendations.
       """,
       tools=[assess_biopsy_indication, assess_hifu_eligibility, compare_treatment_options, generate_treatment_plan, get_patient_education]
   )
   ```

2. **Add to Orchestration** in `api.py`:
   ```python
   if "treatment" in intent or "biopsy" in intent or "hifu" in intent:
       result = treatment_agent.run(...)
   ```

3. **Test Flow:**
   - User asks about biopsy
   - Agent collects data
   - Agent calls tools
   - Agent generates plan
   - Email sent via Fly agent

4. **Frontend (Optional):**
   - Can render TSX components for interactive form
   - OR just use conversational interface
   - OR both (form for initial data, chat for discussion)

---

## Why This Architecture?

✅ **Evidence-based:** Every score has citations  
✅ **Modular:** Calculators are reusable  
✅ **Auditable:** Full reasoning chain visible  
✅ **Privacy-safe:** De-identified outputs  
✅ **Capacity-aware:** Theatre booking intelligence  
✅ **Patient-friendly:** Plain language emails  
✅ **Clinical-grade:** EMR-ready summaries  

**No LiveKit needed** for pure chat workflow - your existing Fly email infrastructure handles everything!

---

## File Structure

```
procedural/
└── procedural_calculators.py    ← New backend calculators

tools.py                          ← Updated with 4 new tools

clinical_graph/
├── biopsy.yaml                   ← Evidence specs (existing)
├── hifu.yaml                     ← Evidence specs (existing)
└── surgical_intake_*.jsx         ← Original form (reference)

TREATMENT_AGENT_ARCHITECTURE.md   ← This file
```

**Ready to integrate!** 🎉
