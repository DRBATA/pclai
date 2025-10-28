"""
Safety Knowledge Base Population Script

This script demonstrates how to add clinical safety items to your knowledge base,
including red flags, signposting, and escalation advice.

IMPORTANT: This creates sample data only. In a production environment, 
all safety guidance should be thoroughly verified by qualified clinicians.
"""
import os
import logging
from dotenv import load_dotenv
from .knowledge_base import SafetyKnowledgeBase, create_vector_search_function

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_sample_data():
    print("--- Executing populate_sample_data function ---")
    """
    Populate the knowledge base with sample safety data.
    
    This is an example function showing how to add various types of
    clinical safety concerns to your database.
    
    In a production environment, you would likely import this data from
    a verified clinical source or have it reviewed by a medical team.
    """
    kb = SafetyKnowledgeBase()
    
    if not kb.is_configured:
        logger.error("Safety knowledge base not configured. Check your environment variables.")
        return False
    
    # First, create the vector similarity search function if it doesn't exist
    create_vector_search_function(kb.supabase)
    
    # Example 1: Red Flag - Chest Pain (High Severity)
    chest_pain_id = kb.add_safety_knowledge(
        category="red_flag",
        subcategory="cardiac",
        title="Acute Chest Pain", 
        description=(
            "Central chest pain, especially when accompanied by shortness of breath, "
            "sweating, pain radiating to jaw/arm, or feeling of impending doom may "
            "indicate a significant cardiac event requiring urgent assessment."
        ),
        severity=5,
        action="999/A&E",
        timeframe="immediate",
        triggers=["chest pain", "chest tightness", "crushing sensation", "chest pressure"],
        wellness_thresholds={"pain": 7, "anxiety": 8},
        symptom_patterns={
            "radiation": ["arm", "jaw", "back"],
            "aggravating_factors": ["exertion", "stress"],
            "relieving_factors": ["rest", "nitroglycerin"]
        },
        body_systems=["cardiovascular", "respiratory"],
        population_specifics={
            "elderly": "May present atypically with fatigue or shortness of breath only",
            "women": "More likely to present with fatigue, dyspnea, or upper back pain",
            "diabetics": "May have minimal or no pain due to neuropathy"
        },
        evidence_level="high",
        source="NICE CG95, AHA Guidelines",
        clinical_pearls=(
            "Remember that diabetic patients may have silent MIs due to autonomic neuropathy. "
            "Absence of chest pain should not rule out cardiac pathology when other red flags present."
        ),
        guideline_limitations=(
            "NICE guidelines on chest pain may miss young patients with coronary anomalies. "
            "Exercise stress tests have limited sensitivity."
        ),
        contextual_interpretation=(
            "For young patients with sharp, pleuritic chest pain worsened by movement or breathing, "
            "musculoskeletal causes are more likely but should still prompt assessment if severe."
        ),
        evidence_quality_notes=(
            "Multiple RCTs support emergent intervention for STEMI; observational data "
            "supports prompt assessment of all acute chest pain presentations."
        )
    )
    
    if chest_pain_id:
        # Add tags for easier filtering and categorization
        kb.add_safety_tags(chest_pain_id, {
            "system": ["cardiovascular", "respiratory"],
            "demographic": ["all", "elderly", "women", "diabetics"],
            "commonality": "common",
            "pathology": ["MI", "ACS", "angina", "aortic dissection", "pulmonary embolism"],
            "symptoms": ["pain", "dyspnea", "diaphoresis", "nausea", "radiation"]
        })
        logger.info(f"Added chest pain red flag with ID: {chest_pain_id}")
    
    # Example 2: Red Flag - Severe Headache (Medium-High Severity)
    headache_id = kb.add_safety_knowledge(
        category="red_flag",
        subcategory="neurological",
        title="Thunderclap Headache",
        description=(
            "Sudden onset severe headache reaching maximum intensity within seconds to minutes. "
            "May indicate subarachnoid hemorrhage, requiring immediate medical attention."
        ),
        severity=4,
        action="999/A&E",
        timeframe="immediate",
        triggers=["sudden headache", "worst headache", "thunderclap", "explosively severe"],
        wellness_thresholds={"pain": 8},
        symptom_patterns={
            "onset": ["sudden", "seconds", "minutes"],
            "associated_features": ["neck stiffness", "photophobia", "vomiting", "altered consciousness"]
        },
        body_systems=["neurological"],
        population_specifics={
            "hypertensive": "Higher risk of hemorrhagic stroke",
            "anticoagulated": "Increased risk of intracranial bleeding"
        },
        evidence_level="high",
        source="NICE Guidelines, American Headache Society",
        clinical_pearls=(
            "Never dismiss a patient-reported 'worst headache of life' - this description has "
            "high positive predictive value for SAH. Absence of neck stiffness does not rule out SAH."
        ),
        guideline_limitations=(
            "CT brain has decreasing sensitivity for SAH over time; negative CT may still "
            "require LP if presentation is delayed >6 hours."
        ),
        contextual_interpretation=(
            "Consider common mimics such as migraine, but err on side of caution with first "
            "presentation of thunderclap headache even with typical migrainous features."
        ),
        evidence_quality_notes=(
            "Observational studies support CT+LP approach; some centers moving towards "
            "CT angiography as alternative to LP with normal CT."
        )
    )
    
    if headache_id:
        kb.add_safety_tags(headache_id, {
            "system": ["neurological"],
            "demographic": ["all", "hypertensive", "anticoagulated"],
            "commonality": "uncommon",
            "pathology": ["SAH", "stroke", "meningitis", "venous sinus thrombosis"],
            "symptoms": ["headache", "photophobia", "vomiting", "stiff neck", "altered consciousness"]
        })
        logger.info(f"Added thunderclap headache red flag with ID: {headache_id}")
    
    # Example 3: Signposting - Night Sweats (Medium Severity)
    night_sweats_id = kb.add_safety_knowledge(
        category="signposting",
        subcategory="systemic",
        title="Persistent Night Sweats",
        description=(
            "Night sweats persisting for more than 2 weeks, especially with weight loss, "
            "fatigue or other systemic symptoms may indicate significant underlying pathology "
            "requiring medical assessment."
        ),
        severity=3,
        action="GP appointment",
        timeframe="within 1 week",
        triggers=["night sweats", "drenching sweats", "night time sweating", "nocturnal hyperhidrosis"],
        wellness_thresholds=None,
        symptom_patterns={
            "associated_features": ["weight loss", "fatigue", "fever", "cough"],
            "duration": ["persistent", "recurrent", "weeks"]
        },
        body_systems=["immune", "endocrine", "respiratory"],
        population_specifics={
            "elderly": "Consider TB and malignancy with higher suspicion",
            "immunosuppressed": "Higher risk of opportunistic infections",
            "women": "Consider perimenopause/menopause in appropriate age group"
        },
        evidence_level="moderate",
        source="NICE CKS, British Thoracic Society",
        clinical_pearls=(
            "While menopause is a common cause in women aged 45-55, don't miss the opportunity "
            "to screen for concurrent TB or lymphoma when other red flags present."
        ),
        guideline_limitations=(
            "Guidelines often recommend multiple investigations that may delay diagnosis. "
            "Consider chest X-ray early in the diagnostic pathway."
        ),
        contextual_interpretation=(
            "The combination of persistent night sweats with weight loss significantly "
            "increases risk of underlying malignancy or chronic infection."
        ),
        evidence_quality_notes=(
            "Limited high-quality evidence for diagnostic pathways; recommendations based "
            "largely on observational studies and expert consensus."
        )
    )
    
    if night_sweats_id:
        kb.add_safety_tags(night_sweats_id, {
            "system": ["immune", "endocrine", "respiratory"],
            "demographic": ["all", "elderly", "immunosuppressed", "women"],
            "commonality": "common",
            "pathology": ["infection", "TB", "lymphoma", "menopause", "thyroid disease"],
            "symptoms": ["sweating", "weight loss", "fever", "fatigue"]
        })
        logger.info(f"Added night sweats signposting with ID: {night_sweats_id}")
    
    # Example 4: Escalation - Abdominal Pain (Medium-High Severity)
    abdominal_pain_id = kb.add_safety_knowledge(
        category="escalation",
        subcategory="abdominal",
        title="Acute Severe Abdominal Pain",
        description=(
            "Acute severe abdominal pain, especially if associated with rigidity, rebound tenderness, "
            "or signs of shock may indicate peritonitis, perforation or other surgical emergency."
        ),
        severity=4,
        action="999/A&E",
        timeframe="immediate",
        triggers=["severe abdominal pain", "rigid abdomen", "rebound tenderness", "guarding"],
        wellness_thresholds={"pain": 8},
        symptom_patterns={
            "onset": ["acute", "sudden", "hours"],
            "character": ["severe", "constant", "worsening"],
            "associated_features": ["vomiting", "fever", "distension", "absent bowel sounds"]
        },
        body_systems=["gastrointestinal"],
        population_specifics={
            "elderly": "May present atypically with minimal pain despite serious pathology",
            "immunosuppressed": "May have minimal inflammatory response",
            "women": "Consider gynecological causes including ectopic pregnancy"
        },
        evidence_level="high",
        source="NICE Guidelines, Royal College of Surgeons",
        clinical_pearls=(
            "The combination of pain out of proportion to examination and inability to find a comfortable "
            "position ('restlessness') should raise suspicion for mesenteric ischemia, especially in elderly "
            "patients with cardiovascular risk factors."
        ),
        guideline_limitations=(
            "Guidelines may overemphasize diagnostic imaging, potentially delaying surgical intervention "
            "in clear cases of peritonitis where clinical diagnosis should prompt action."
        ),
        contextual_interpretation=(
            "Elderly patients with acute abdominal pain have higher mortality; lower threshold for "
            "referral is appropriate even if signs are subtle."
        ),
        evidence_quality_notes=(
            "Strong observational evidence supports prompt surgical assessment of acute abdomen; "
            "specific diagnostic algorithms have variable evidence quality."
        )
    )
    
    if abdominal_pain_id:
        kb.add_safety_tags(abdominal_pain_id, {
            "system": ["gastrointestinal"],
            "demographic": ["all", "elderly", "immunosuppressed", "women"],
            "commonality": "common",
            "pathology": ["appendicitis", "perforation", "bowel obstruction", "ischemia", "diverticulitis"],
            "symptoms": ["pain", "vomiting", "fever", "distension", "constipation"]
        })
        logger.info(f"Added abdominal pain escalation with ID: {abdominal_pain_id}")

    # -------------------------------------------------------------
    # Escalation Advice Items derived from user-supplied markdown
    # -------------------------------------------------------------

    # 1. Severe musculoskeletal injury requiring immediate care
    msk_severe_id = kb.add_safety_knowledge(
        category="escalation",
        subcategory="musculoskeletal",
        title="Severe Musculoskeletal Injury – Immediate Assessment",
        description=(
            "Severe pain rated 8–10/10, inability to bear weight, obvious deformity, major swelling or "
            "associated numbness following trauma suggests possible fracture, dislocation or neurovascular "
            "compromise and warrants same-day assessment in A&E or a Minor Injury Unit."
        ),
        severity=4,
        action="A&E / MIU",
        timeframe="immediate",
        triggers=[
            "severe limb pain", "cannot bear weight", "gross deformity", "severe swelling", "post-traumatic numbness"
        ],
        body_systems=["musculoskeletal"],
        evidence_level="consensus",
        source="User escalation ladder markdown"
    )
    if msk_severe_id:
        kb.add_safety_tags(msk_severe_id, {
            "system": ["musculoskeletal"],
            "severity": "severe",
            "setting": "injury",
            "symptoms": ["pain", "deformity", "swelling", "numbness"]
        })
        logger.info(f"Added musculoskeletal severe escalation with ID: {msk_severe_id}")

    # 2. Mild–moderate musculoskeletal injury monitoring advice
    msk_mild_id = kb.add_safety_knowledge(
        category="escalation",
        subcategory="musculoskeletal",
        title="Mild-Moderate Musculoskeletal Injury – Monitor then GP/FCP",
        description=(
            "Pain ≤7/10 and swelling improving within 48 h can generally be managed with rest, ice, compression "
            "and elevation. If pain or function does not improve after 48 h, arrange review with First Contact "
            "Physiotherapist (FCP) or GP."
        ),
        severity=2,
        action="Monitor → FCP / GP if no improvement",
        timeframe="48 h",
        triggers=["mild limb pain", "minor swelling"],
        body_systems=["musculoskeletal"],
        evidence_level="consensus",
        source="User escalation ladder markdown"
    )
    if msk_mild_id:
        kb.add_safety_tags(msk_mild_id, {
            "system": ["musculoskeletal"],
            "severity": "mild_moderate",
            "setting": "injury",
            "symptoms": ["pain", "swelling"]
        })
        logger.info(f"Added musculoskeletal monitor advice with ID: {msk_mild_id}")

    # 3. Headache escalation criteria
    headache_escalate_id = kb.add_safety_knowledge(
        category="escalation",
        subcategory="neurological",
        title="Headache – Escalation Criteria",
        description=(
            "Escalate to A&E or urgent GP for any sudden ‘worst ever’ headache, associated fever with neck stiffness, "
            "neurological signs, headache post-head-injury, or a progressively worsening pattern. Otherwise, encourage "
            "hydration and OTC analgesia, and arrange GP review if persisting >72 h."
        ),
        severity=3,
        action="A&E / Urgent GP",
        timeframe="immediate if red-flag; otherwise 72 h GP",
        triggers=["worst headache", "fever", "neck stiffness", "neuro deficit", "post head injury"],
        body_systems=["neurological"],
        evidence_level="consensus",
        source="User escalation ladder markdown"
    )
    if headache_escalate_id:
        kb.add_safety_tags(headache_escalate_id, {
            "system": ["neurological"],
            "symptoms": ["headache", "fever", "neck stiffness", "neurological deficit"],
            "commonality": "common"
        })
        logger.info(f"Added headache escalation with ID: {headache_escalate_id}")

    # 4. Respiratory / chest pain escalation advice
    chest_pain_escalate_id = kb.add_safety_knowledge(
        category="escalation",
        subcategory="respiratory",
        title="Crushing Chest Pain with Breathlessness",
        description=(
            "Crushing central chest pain with breathlessness at rest should trigger an immediate 999 call. "
            "Possible acute coronary syndrome or massive pulmonary embolism."),
        severity=5,
        action="999",
        timeframe="immediate",
        triggers=["crushing chest pain", "rest breathlessness"],
        body_systems=["cardiovascular", "respiratory"],
        evidence_level="high",
        source="User escalation ladder markdown"
    )
    if chest_pain_escalate_id:
        kb.add_safety_tags(chest_pain_escalate_id, {
            "system": ["cardiovascular", "respiratory"],
            "symptoms": ["pain", "dyspnea"],
            "severity": "severe"
        })
        logger.info(f"Added chest pain escalation with ID: {chest_pain_escalate_id}")

    # 5. Escalation ladder – general guidance
    ladder_id = kb.add_safety_knowledge(
        category="escalation",
        subcategory="general",
        title="Five-Step Escalation Ladder",
        description=(
            "Step-wise model: 1) Self-care – OTC meds & rest; 2) Pharmacist – symptom advice; 3) GP/FCP – diagnostics; "
            "4) MIU/Urgent Care – same-day injury / illness not life-threatening; 5) A&E/999 – immediate threat to life, "
            "limb or sight. Patients should climb sooner if symptoms worsen or new red flags appear."),
        severity=1,
        action="Follow step-wise escalation",
        timeframe="variable",
        triggers=["worsening symptoms", "new red flags"],
        body_systems=["general"],
        evidence_level="consensus",
        source="User escalation ladder markdown"
    )
    if ladder_id:
        kb.add_safety_tags(ladder_id, {
            "type": "process",
            "audience": "all"
        })
        logger.info(f"Added general escalation ladder with ID: {ladder_id}")

    return True

if __name__ == "__main__":
    # When run directly, populate the database with sample data
    populate_sample_data()
