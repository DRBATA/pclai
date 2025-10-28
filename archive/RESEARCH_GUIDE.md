# Phase 1: Research Guide

This guide will help you find evidence-based data to replace the `TODO: RESEARCH` placeholders in `urology_calculator.py`.

## Priority Order

1. **Priors (Epidemiology)** - Foundation for all calculations
2. **Symptom Points** - Most discriminating symptoms first
3. **Likelihood Functions** - Fine-tuning parameters

---

## 1. PRIORS: Epidemiological Data

### UTI Prevalence
**Search terms:** "urinary tract infection epidemiology prevalence"

**Key sources:**
- Foxman B. "Epidemiology of urinary tract infections" Am J Med 2002;113:5S-13S
- Nicolle LE. "Epidemiology of urinary tract infection" Infect Med 2001

**Data needed:**
- [ ] Baseline prevalence in women: _____% (currently 30%)
- [ ] Baseline prevalence in men: _____% (currently 5%)
- [ ] Age adjustments: _____ 
- [ ] Citation: _________________________________

### BPH Prevalence by Age
**Search terms:** "benign prostatic hyperplasia prevalence age"

**Key sources:**
- Berry SJ et al. "The development of human benign prostatic hyperplasia with age" JAMA 1984;251(7):857-862
- EAU Guidelines on Management of Non-Neurogenic Male LUTS

**Data needed:**
- [ ] Age 40-49: _____% (currently 10%)
- [ ] Age 50-59: _____% (currently 25%)
- [ ] Age 60-69: _____% (currently 50%)
- [ ] Age 70+: _____% (currently 70%)
- [ ] Citation: _________________________________

### Prostate Cancer Risk
**Search terms:** "prostate cancer lifetime risk age family history"

**Key sources:**
- Cancer Research UK statistics
- SEER database (seer.cancer.gov)
- Johns Hopkins Prostate Cancer genetics

**Data needed:**
- [ ] Baseline age 50: _____% (currently 2%)
- [ ] Baseline age 65: _____% (currently 8%)
- [ ] With family history: _____% (currently 15%)
- [ ] Citation: _________________________________

### Overactive Bladder
**Search terms:** "overactive bladder prevalence epidemiology"

**Key sources:**
- Irwin et al. BJU Int 2006;97(2):247-250
- Stewart et al. World J Urol 2003;20(6):327-336

**Data needed:**
- [ ] General population: _____% (currently 16%)
- [ ] Female: _____% (currently 18%)
- [ ] Male: _____% (currently 14%)
- [ ] Citation: _________________________________

### Kidney Stones
**Search terms:** "kidney stone prevalence recurrence rate"

**Key sources:**
- UpToDate: "Epidemiology of nephrolithiasis"
- Scales et al. Eur Urol 2012;62(1):160-165

**Data needed:**
- [ ] General population: _____% (currently 10%)
- [ ] Recurrence rate: _____% (currently 50%)
- [ ] Citation: _________________________________

### Interstitial Cystitis / Painful Bladder Syndrome
**Search terms:** "interstitial cystitis prevalence IC/PBS epidemiology"

**Key sources:**
- Berry et al. J Urol 2011;186(2):540-544
- Rosenberg et al. Int Urogynecol J 2007;18(8):919-924

**Data needed:**
- [ ] General population: _____% (currently 3%)
- [ ] Female: _____% (currently 5%)
- [ ] Male: _____% (currently 1%)
- [ ] Citation: _________________________________

---

## 2. SYMPTOM POINTS: Likelihood Ratios

### Critical: Dysuria (Pain/Burning on Urination)
**Search terms:** "dysuria sensitivity specificity urinary tract infection"

**Key sources:**
- Bent S et al. "Does this woman have an acute uncomplicated urinary tract infection?" JAMA 2002;287(20):2701-2710
- Little P et al. BMJ 2010;340:c199

**Data needed:**
- [ ] Sensitivity for UTI: _____%
- [ ] Specificity for UTI: _____%
- [ ] Positive LR: _____
- [ ] Convert to log-odds points: _____
- [ ] Citation: _________________________________

**How to convert:**
```
If LR+ = 3.5, then log_odds_points = ln(3.5) ≈ 1.25
Multiply by weight factor (e.g., 2-4) for clinical significance
```

### Critical: Sudden vs Gradual Onset
**Search terms:** "acute vs chronic urinary symptoms presentation"

**Key sources:**
- Clinical textbooks on urological diagnosis
- NICE Guidelines CKS on urinary symptoms

**Data needed:**
- [ ] % of UTI patients with sudden onset: _____%
- [ ] % of BPH patients with gradual onset: _____%
- [ ] Convert to points for each condition
- [ ] Citation: _________________________________

### Hematuria (Blood in Urine)
**Search terms:** "hematuria differential diagnosis likelihood"

**Key sources:**
- Davis R et al. Am Fam Physician 2008;78(3):347-352
- EAU Guidelines on Hematuria

**Data needed:**
- [ ] Stones: Prevalence with hematuria _____%
- [ ] Cancer: Prevalence with painless hematuria _____%
- [ ] UTI: Prevalence with hematuria _____%
- [ ] Citation: _________________________________

### Fever in Urological Conditions
**Search terms:** "febrile urinary tract infection pyelonephritis"

**Data needed:**
- [ ] % of UTIs that are febrile: _____%
- [ ] % of BPH with fever: _____%
- [ ] % of prostatitis with fever: _____%
- [ ] Citation: _________________________________

---

## 3. LIKELIHOOD FUNCTIONS: Parameter Tuning

### Dysuria Severity Curve
**Current formula:** `1 / (1 + exp(-0.15 * (severity - 30)))`

**Research needed:**
- [ ] At what pain level (0-100) is UTI highly likely? _____
- [ ] What's the typical pain range for UTI dysuria? _____
- [ ] Adjust sigmoid steepness parameter: _____ (currently 0.15)
- [ ] Adjust center point: _____ (currently 30)

### Weak Stream and BPH
**Current formula:** `0.3/(1+exp(-0.1*(x-40))) + 0.6*exp(-(x-80)²/300)`

**Research needed:**
- [ ] IPSS Question 1 correlation with BPH diagnosis
- [ ] What IPSS score suggests moderate BPH? _____
- [ ] What IPSS score suggests severe BPH? _____
- [ ] Adjust curve parameters accordingly

---

## Research Workflow

### Step 1: PubMed Search
```
1. Go to pubmed.ncbi.nlm.nih.gov
2. Search each term above
3. Filter by: Review articles, Meta-analyses, Clinical trials
4. Look for papers from last 10 years
```

### Step 2: Clinical Guidelines
```
1. NICE CKS (cks.nice.org.uk)
2. EAU Guidelines (uroweb.org/guidelines)
3. AUA Guidelines (auanet.org/guidelines-and-quality)
```

### Step 3: UpToDate (if you have access)
```
1. Search condition name
2. Look for "Epidemiology" and "Clinical presentation" sections
3. Check cited references
```

### Step 4: Document in Code
```python
# Example format:
UROLOGY_PRIORS = {
    "uti": {
        "female_baseline": 0.26,  # Foxman 2002: 26% lifetime risk in women
        "male_baseline": 0.04,   # Foxman 2002: 4% lifetime risk in men
        "citation": "Foxman B. Am J Med 2002;113:5S-13S"
    }
}
```

---

## Quick Wins (Start Here)

If time is limited, prioritize these:

1. **BPH prevalence by age** - Berry et al study (very well established)
2. **Dysuria for UTI** - Bent et al JAMA 2002 (classic study)
3. **Sudden onset** - Common clinical knowledge, any UTI guidelines
4. **Hematuria** - Well documented in urology textbooks

---

## Notes

- Don't aim for perfection - approximations from good sources are fine
- Focus on **relative** differences between conditions
- If you find a range, use the middle value
- Document EVERY source - this is critical for credibility
- When unsure, conservative estimates are safer

---

## Example: Completed Entry

```python
"dysuria": {
    "uti": 4,  # Bent et al 2002: LR+ = 3.5 for dysuria in UTI
    "prostatitis": 3,  # Clinical experience: also common
    "kidney_stones": 1,  # Less specific
    "ic": 3,  # Chronic dysuria is hallmark
    "bph": -1,  # Usually painless voiding
    "oab": -2,  # Urgency without pain
    "prostate_cancer": -1,  # Usually painless
    "citation": "Bent S et al. JAMA 2002;287(20):2701-2710. Dysuria LR+ 1.5-3.5 for UTI in women"
}
```
