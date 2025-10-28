"""
Clinical Education Content
In-depth explanations for common patient questions and concerns
These are used by agents when explaining results, risks, and options
"""

CLINICAL_EDUCATION = {
    "psa_normal_doesnt_rule_out_cancer": {
        "title": "Does a Normal PSA Rule Out Prostate Cancer?",
        "short_answer": "No, a normal PSA does NOT rule out prostate cancer. 15% of men with PSA < 4.0 ng/mL have prostate cancer.",
        "content": """
No, a normal PSA **does not** rule out prostate cancer. This is one of the most dangerous and persistent misconceptions in men's health.

Relying on a "normal" PSA result for reassurance can lead to missed diagnoses of significant cancers.

### The Core Problem: PSA is Sensitive, but Not Perfect

Think of PSA not as a light switch (cancer = on, no cancer = off), but as a **smoke detector**. It's very good at detecting when something *might* be wrong, but it can also be silent in the presence of a real fire, and it can be triggered by non-threatening smoke (like benign prostatic hyperplasia or prostatitis).

A "normal" PSA is typically defined as **below 4.0 ng/mL**. However, this threshold is an arbitrary cutoff designed for population-level screening, not for individual diagnosis.

### The Evidence: How Common is Cancer with a "Normal" PSA?

The landmark **Prostate Cancer Prevention Trial (PCPT)** provided the most definitive answer. In this trial, all men, regardless of their PSA level, were offered a prostate biopsy at the end of the study.

**The findings were staggering:**
- **15% of men with a PSA < 4.0 ng/mL were found to have prostate cancer.**
- **Approximately 15% of those cancers (about 2.3% of the total group) were high-grade (Gleason ≥ 7).**

**Source:** Thompson IM, et al. "Prevalence of Prostate Cancer among Men with a Prostate-Specific Antigen Level ≤ 4.0 ng per Milliliter." *N Engl J Med*. 2004;350(22):2239-2246.

This means that if you only rely on the PSA < 4.0 threshold, you will miss a significant number of cancers, including some that are aggressive and require treatment.

### Why is PSA "Normal" in Some Men with Cancer?

1. **Low-Volume or Indolent Tumors:** A very small cancer may not produce enough PSA to cross the 4.0 ng/mL threshold.
2. **Poorly Differentiated Tumors:** Paradoxically, some very aggressive, high-grade (Gleason 9-10) cancers are so "undifferentiated" that they lose the ability to produce much PSA. They are dangerous but "PSA-silent."
3. **Individual Baseline:** A man with a naturally low baseline PSA (e.g., always around 0.8 ng/mL) might have a significant cancer that only raises his PSA to 2.5 ng/mL. While this is technically "normal," the *tripling* of his PSA is a major red flag that would be missed without prior history.

### High-Risk Scenarios Where a "Normal" PSA is Especially Misleading

| Scenario | Why PSA is Misleading | What to Do Next |
|----------|----------------------|-----------------|
| **Strong Family History** | Men with a father or brother diagnosed with prostate cancer, especially before age 65, have a genetically higher risk. Their cancers may develop at lower PSA levels. | Consider a baseline MRI. Discuss PSA density and velocity. Start screening earlier (age 40-45). |
| **African Ancestry** | Men of African descent have a higher incidence of prostate cancer and are more likely to develop aggressive disease at a younger age and at lower PSA levels. | Strongly consider a baseline MRI, even with PSA < 2.5. Use race-adjusted risk calculators. |
| **Suspicious Digital Rectal Exam (DRE)** | A DRE can detect hard, irregular nodules on the prostate that are characteristic of cancer. These tumors may be located anteriorly (in the front) and not elevate PSA significantly. | **A suspicious DRE should prompt a biopsy, regardless of PSA level.** |
| **Rising PSA Trend (PSA Velocity)** | A man whose PSA has steadily risen from 0.5 to 1.5 to 2.8 ng/mL over three years is a major concern, even though 2.8 is "normal." A velocity > 0.35 ng/mL/year is a red flag. | Investigate the trend. Calculate PSA density. Strongly consider an MRI. |
| **Low Free/Total PSA Ratio** | The percentage of PSA that is "free" (unbound) is lower in men with cancer. A total PSA of 3.5 with a free PSA of 8% is more suspicious than a total PSA of 3.5 with a free PSA of 25%. | If total PSA is 2.5-10.0, a reflex test for free PSA is essential. A low ratio (<10%) is an indication for biopsy. |

### The Modern Approach: Moving Beyond a Single PSA Number

The decision to investigate for prostate cancer is no longer based on a single PSA number. It is a **combinatorial assessment** that creates a more accurate "topological space of risk."

1. **PSA is the starting point, not the end point.**
2. **Context is King:** Family history, race, age, and symptoms are factored in.
3. **PSA Kinetics:** Velocity and density are calculated.
4. **Secondary Biomarkers:** If risk is intermediate, tests like the **PHI** or **4Kscore** can be used to better differentiate between benign and cancerous conditions.
5. **Multiparametric MRI (mpMRI):** This is the game-changer. An MRI can visualize suspicious lesions inside the prostate and assign them a **PI-RADS score**. A man with a PSA of 2.5 but a PI-RADS 4 lesion is at high risk for significant cancer and needs a targeted biopsy. A man with a PSA of 5.0 but a negative MRI (PI-RADS 1-2) may be able to safely avoid biopsy.

### The Bottom Line

A normal PSA **does not rule out prostate cancer**. It is a population screening tool that must be interpreted within a rich clinical context. For men at higher risk or with other clinical red flags, a "normal" PSA can be falsely reassuring and dangerously misleading.

The modern, evidence-based approach is to use PSA as a trigger for a more sophisticated risk assessment, which increasingly involves **multiparametric MRI** as the key decision-making tool before considering a biopsy.
""",
        "key_points": [
            "15% of men with PSA < 4.0 have prostate cancer (PCPT trial)",
            "Some aggressive cancers are 'PSA-silent'",
            "Family history and ethnicity increase risk even with normal PSA",
            "PSA velocity (trend) more important than single value",
            "Multiparametric MRI is now the key decision tool"
        ]
    },
    
    "elevated_psa_causes": {
        "title": "What Causes an Elevated PSA Besides Cancer?",
        "short_answer": "PSA can be elevated by infection, BPH, recent ejaculation, cycling, or prostate manipulation. Test for infection first.",
        "content": """
An elevated PSA does not automatically mean cancer. Many benign conditions can raise PSA levels, sometimes dramatically.

### Common Benign Causes of Elevated PSA:

**1. Benign Prostatic Hyperplasia (BPH)**
- As the prostate enlarges with age, more PSA-producing cells are present
- Can elevate PSA to 4-10 ng/mL range
- Check PSA density: PSA / prostate volume (measured by ultrasound)

**2. Prostatitis (Prostate Infection/Inflammation)**
- Bacterial or non-bacterial inflammation
- Can cause dramatic PSA elevations (10-50+ ng/mL)
- **KEY:** Treat the infection first, then recheck PSA in 4-6 weeks
- PSA should drop significantly if infection was the cause

**3. Urinary Tract Infection (UTI)**
- Bladder infection can cause mild PSA elevation
- Always do a urine dipstick before worrying about PSA

**4. Recent Sexual Activity**
- Ejaculation can temporarily raise PSA
- Avoid sexual activity for 48 hours before PSA test

**5. Recent Cycling or Exercise**
- Vigorous cycling or exercise can cause mild elevation
- Avoid for 24-48 hours before test

**6. Digital Rectal Exam (DRE)**
- Prostate manipulation can elevate PSA slightly
- Some guidelines suggest drawing PSA *before* DRE

**7. Recent Catheterization or Cystoscopy**
- Instrumentation of the urethra can elevate PSA
- Wait 1-2 weeks after procedure before testing

### The Diagnostic Approach:

```
Elevated PSA → Check for UTI (urine dipstick)
    ↓
If UTI present → Treat with antibiotics → Recheck PSA in 4-6 weeks
    ↓
If no UTI but symptoms of prostatitis → Trial of antibiotics → Recheck
    ↓
If persistently elevated and no infection → Calculate:
    - PSA velocity (change over time)
    - PSA density (PSA / prostate volume)
    - Free/Total PSA ratio
    ↓
If still concerning → Multiparametric MRI → Targeted biopsy if PI-RADS ≥ 3
```

### Why This Matters:

Testing for and treating infection FIRST can avoid unnecessary biopsies. Many men have been biopsied for a PSA of 8 ng/mL that drops to 2 ng/mL after treating prostatitis.

**Always rule out benign causes before assuming cancer.**
""",
        "key_points": [
            "BPH, prostatitis, UTI are common benign causes",
            "Treat infection first, then recheck PSA in 4-6 weeks",
            "Avoid ejaculation, cycling, DRE before PSA test",
            "PSA density and velocity add context",
            "MRI before biopsy is now preferred pathway"
        ]
    },
    
    "surgery_avoidance_bph": {
        "title": "Can I Avoid Surgery for BPH?",
        "short_answer": "Yes, most men with BPH can manage symptoms with medications. Surgery is only needed if medications fail or complications develop.",
        "content": """
Most men with Benign Prostatic Hyperplasia (BPH) can successfully manage their symptoms **without surgery**. Surgery is reserved for severe cases or when medications fail.

### The Stepwise Approach:

**1. Watchful Waiting (Mild Symptoms - IPSS < 8)**
- If symptoms are minimal and not bothersome
- No intervention needed
- Monitor symptoms annually

**2. Lifestyle Modifications**
- Reduce caffeine and alcohol
- Avoid drinking large amounts before bed
- Double voiding technique
- Bladder training

**3. Medications (Moderate Symptoms - IPSS 8-19)**

**Alpha-Blockers** (First-line)
- Tamsulosin (Flomax), Alfuzosin, Doxazosin
- Relax smooth muscle in prostate and bladder neck
- Work within days to weeks
- Side effects: Dizziness, retrograde ejaculation

**5-Alpha Reductase Inhibitors** (For larger prostates)
- Finasteride, Dutasteride
- Shrink the prostate over 6-12 months
- Reduce PSA by ~50% (important for cancer screening)
- Side effects: Decreased libido, erectile dysfunction (5-10% of men)

**Combination Therapy**
- Alpha-blocker + 5-ARI for large prostates
- Most effective medical therapy

**4. Surgery (Only When Needed - IPSS ≥ 20 or Complications)**

Indications for surgery:
- Recurrent urinary retention despite medications
- Recurrent UTIs due to incomplete emptying
- Bladder stones from retention
- Kidney damage from back-pressure
- Severe symptoms not responding to medications
- Patient preference after informed discussion

### Success Rates:

**Medications:**
- 60-80% of men see significant symptom improvement
- Can continue for years without progression

**Surgery:**
- >90% symptom improvement
- But carries risks: bleeding, infection, incontinence (5%), erectile dysfunction (10%)

### The Bottom Line:

**You can almost certainly avoid surgery if:**
- You're willing to take daily medications
- Your symptoms are moderate (not causing kidney damage)
- You don't have recurrent retention or infections

**Surgery should be a last resort**, not a first option. Discuss medication trials thoroughly before considering surgical intervention.
""",
        "key_points": [
            "60-80% of men improve with medications alone",
            "Alpha-blockers work quickly, 5-ARIs shrink prostate slowly",
            "Combination therapy most effective",
            "Surgery only for severe symptoms or complications",
            "Medications can be continued long-term safely"
        ]
    }
}


def get_education_content(topic_key: str) -> dict:
    """
    Retrieve educational content for a specific topic
    
    Args:
        topic_key: The key for the educational topic
        
    Returns:
        Dict with title, short_answer, content, and key_points
    """
    return CLINICAL_EDUCATION.get(topic_key, {
        "title": "Topic not found",
        "short_answer": "",
        "content": "",
        "key_points": []
    })


def search_education_topics(query: str) -> list[str]:
    """
    Search for relevant educational topics based on query
    
    Args:
        query: Search query (e.g., "PSA", "prostate", "surgery")
        
    Returns:
        List of matching topic keys
    """
    query_lower = query.lower()
    matches = []
    
    for key, content in CLINICAL_EDUCATION.items():
        title = content["title"].lower()
        short = content["short_answer"].lower()
        
        if query_lower in title or query_lower in short or query_lower in key:
            matches.append(key)
    
    return matches
