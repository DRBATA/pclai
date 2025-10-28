#!/usr/bin/env python3
"""
Test script for Urology Bayesian Calculator
Run this to test the calculator with example cases
"""

import sys
import json
from differentials.urology_calculator import (
    compute_urology_differential,
    calculate_entropy
)

def print_result(title, result):
    """Pretty print results"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")
    print(json.dumps(result, indent=2))

def test_case_1_uti():
    """Test Case 1: Young woman with acute UTI symptoms"""
    print("\n" + "="*80)
    print("TEST CASE 1: Young Woman with Acute UTI Symptoms")
    print("="*80)
    
    patient_info = {
        "age": 28,
        "gender": "female"
    }
    
    symptoms = {
        "onset_speed": "sudden",  # Started yesterday
        "dysuria": True,
        "dysuria_severity": 75,   # 7.5/10 pain
        "reported_symptoms": ["pain_burning", "urgency"],
        "fever_present": False,
        "nocturia_per_night": 2
    }
    
    result = compute_urology_differential(symptoms, patient_info)
    
    print(f"\nPatient: {patient_info['age']}-year-old {patient_info['gender']}")
    print(f"Symptoms: {symptoms['reported_symptoms']}")
    print(f"Onset: {symptoms['onset_speed']} (dysuria severity {symptoms['dysuria_severity']}/100)")
    
    print("\n--- PROBABILITIES ---")
    for condition, prob in sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {condition:25} {prob:6.1%}")
    
    entropy = calculate_entropy(result["probabilities"])
    print(f"\nEntropy: {entropy:.3f}")
    
    print("\n--- RECOMMENDATION ---")
    rec = result["recommendation"]
    print(f"  Primary: {rec['primary_diagnosis']}")
    print(f"  Confidence: {rec['confidence']}")
    print(f"  Action: {rec['action']}")
    print(f"  Urgency: {rec['urgency']}")
    
    return result

def test_case_2_bph():
    """Test Case 2: Elderly man with gradual BPH symptoms"""
    print("\n" + "="*80)
    print("TEST CASE 2: Elderly Man with Gradual BPH Symptoms")
    print("="*80)
    
    patient_info = {
        "age": 72,
        "gender": "male"
    }
    
    symptoms = {
        "onset_speed": "gradual",  # Over 5 years
        "weak_stream_severity": 85,  # Almost always weak
        "reported_symptoms": ["weak_stream", "nocturia"],
        "nocturia_per_night": 4,
        "fever_present": False,
        "dysuria": False
    }
    
    result = compute_urology_differential(symptoms, patient_info)
    
    print(f"\nPatient: {patient_info['age']}-year-old {patient_info['gender']}")
    print(f"Symptoms: {symptoms['reported_symptoms']}")
    print(f"Onset: {symptoms['onset_speed']} (weak stream severity {symptoms['weak_stream_severity']}/100)")
    
    print("\n--- PROBABILITIES ---")
    for condition, prob in sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {condition:25} {prob:6.1%}")
    
    entropy = calculate_entropy(result["probabilities"])
    print(f"\nEntropy: {entropy:.3f}")
    
    print("\n--- RECOMMENDATION ---")
    rec = result["recommendation"]
    print(f"  Primary: {rec['primary_diagnosis']}")
    print(f"  Confidence: {rec['confidence']}")
    print(f"  Action: {rec['action']}")
    if "suitable_procedures" in rec:
        print(f"  Procedures: {', '.join(rec['suitable_procedures'])}")
    print(f"  Urgency: {rec['urgency']}")
    
    return result

def test_case_3_kidney_stones():
    """Test Case 3: Man with acute kidney stone symptoms"""
    print("\n" + "="*80)
    print("TEST CASE 3: Man with Acute Kidney Stone Symptoms")
    print("="*80)
    
    patient_info = {
        "age": 45,
        "gender": "male",
        "previous_kidney_stones": True  # High recurrence risk
    }
    
    symptoms = {
        "onset_speed": "sudden",  # Started 2 hours ago
        "pain_severity": 95,  # 9.5/10 pain (worst ever)
        "reported_symptoms": ["severe_pain", "blood_in_urine"],
        "hematuria": True,
        "fever_present": False,
        "dysuria": False
    }
    
    result = compute_urology_differential(symptoms, patient_info)
    
    print(f"\nPatient: {patient_info['age']}-year-old {patient_info['gender']}")
    print(f"Symptoms: {symptoms['reported_symptoms']}")
    print(f"Onset: {symptoms['onset_speed']} (pain severity {symptoms['pain_severity']}/100)")
    print(f"History: Previous kidney stones")
    
    print("\n--- PROBABILITIES ---")
    for condition, prob in sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {condition:25} {prob:6.1%}")
    
    entropy = calculate_entropy(result["probabilities"])
    print(f"\nEntropy: {entropy:.3f}")
    
    print("\n--- RECOMMENDATION ---")
    rec = result["recommendation"]
    print(f"  Primary: {rec['primary_diagnosis']}")
    print(f"  Confidence: {rec['confidence']}")
    print(f"  Action: {rec['action']}")
    print(f"  Urgency: {rec['urgency']}")
    
    return result

def test_case_4_prostatitis():
    """Test Case 4: Man with acute prostatitis (fever + dysuria)"""
    print("\n" + "="*80)
    print("TEST CASE 4: Man with Acute Prostatitis (Fever + Dysuria)")
    print("="*80)
    
    patient_info = {
        "age": 52,
        "gender": "male"
    }
    
    symptoms = {
        "onset_speed": "sudden",  # Started yesterday
        "dysuria": True,
        "dysuria_severity": 70,
        "fever_present": True,  # KEY: Fever rules out BPH!
        "reported_symptoms": ["pain_burning", "pelvic_pain"],
        "nocturia_per_night": 3
    }
    
    result = compute_urology_differential(symptoms, patient_info)
    
    print(f"\nPatient: {patient_info['age']}-year-old {patient_info['gender']}")
    print(f"Symptoms: {symptoms['reported_symptoms']}")
    print(f"Onset: {symptoms['onset_speed']}")
    print(f"FEVER: YES (critical finding!)")
    
    print("\n--- PROBABILITIES ---")
    for condition, prob in sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {condition:25} {prob:6.1%}")
    
    entropy = calculate_entropy(result["probabilities"])
    print(f"\nEntropy: {entropy:.3f}")
    
    print("\n--- RECOMMENDATION ---")
    rec = result["recommendation"]
    print(f"  Primary: {rec['primary_diagnosis']}")
    print(f"  Confidence: {rec['confidence']}")
    print(f"  Action: {rec['action']}")
    print(f"  Urgency: {rec['urgency']}")
    
    return result

def test_case_5_uncertain():
    """Test Case 5: Uncertain case - needs more questions"""
    print("\n" + "="*80)
    print("TEST CASE 5: Uncertain Case - Needs More Information")
    print("="*80)
    
    patient_info = {
        "age": 55,
        "gender": "male"
    }
    
    symptoms = {
        "reported_symptoms": ["urgency", "frequency"],
        # Minimal information - no onset speed, no fever, no pain
    }
    
    result = compute_urology_differential(symptoms, patient_info)
    
    print(f"\nPatient: {patient_info['age']}-year-old {patient_info['gender']}")
    print(f"Symptoms: {symptoms['reported_symptoms']}")
    print(f"Note: Minimal information provided")
    
    print("\n--- PROBABILITIES ---")
    for condition, prob in sorted(result["probabilities"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {condition:25} {prob:6.1%}")
    
    entropy = calculate_entropy(result["probabilities"])
    print(f"\nEntropy: {entropy:.3f} (HIGH - very uncertain)")
    
    print("\n--- RECOMMENDATION ---")
    rec = result["recommendation"]
    print(f"  Primary: {rec['primary_diagnosis']}")
    print(f"  Confidence: {rec['confidence']}")
    print(f"  Action: {rec['action']}")
    print(f"  Note: {rec.get('note', 'N/A')}")
    
    return result

def main():
    """Run all test cases"""
    print("\n" + "="*80)
    print("UROLOGY BAYESIAN CALCULATOR - TEST SUITE")
    print("="*80)
    
    results = []
    
    try:
        results.append(("UTI", test_case_1_uti()))
        results.append(("BPH", test_case_2_bph()))
        results.append(("Kidney Stones", test_case_3_kidney_stones()))
        results.append(("Prostatitis", test_case_4_prostatitis()))
        results.append(("Uncertain", test_case_5_uncertain()))
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        for name, result in results:
            top_condition = max(result["probabilities"].items(), key=lambda x: x[1])
            entropy = calculate_entropy(result["probabilities"])
            print(f"\n{name:20} → {top_condition[0]:20} ({top_condition[1]:5.1%}) [Entropy: {entropy:.3f}]")
        
        print("\n" + "="*80)
        print("✅ All tests completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
