"""
Safety Knowledge Base Integration Examples

This file provides examples of how to integrate the safety knowledge base
with your existing agents. These are code snippets that show patterns
you can use within your agent handlers.
"""
import json
from typing import Dict, List, Any, Optional
from .safety_service import safety_service

"""
Example 1: Host Agent Safety Checks

The Host agent collects symptoms and performs initial safety triage.
"""
def host_agent_safety_check(conversation_state, user_symptoms):
    """
    Example Host agent safety check function.
    
    Args:
        conversation_state: The current conversation state
        user_symptoms: Reported symptoms from user
        
    Returns:
        Updated conversation state with safety concerns
    """
    # Get current context or initialize if not present
    context = conversation_state.get('context', {})
    
    # Perform safety check on symptoms
    safety_result = safety_service.check_safety(
        symptoms=user_symptoms
    )
    
    # Record any safety concerns in a structured way
    if safety_result.concerns:
        # Initialize safety concerns array if not present
        if 'safety_concerns' not in context:
            context['safety_concerns'] = []
            
        # Add each concern with Host agent analysis
        for concern in safety_result.concerns:
            context['safety_concerns'].append({
                'id': concern.id,
                'title': concern.title,
                'severity': concern.severity,
                'agent_analysis': f"HOST ANALYSIS: Found potential {concern.category} during initial symptom triage. {concern.clinical_pearls or ''}",
                'assessment_status': "pending",
                'reviewed_by': ["Host"]
            })
        
        # Update clinical assessment
        context['safety_clinical_assessment'] = (
            f"HOST INITIAL ASSESSMENT: Identified {len(safety_result.concerns)} potential safety concerns. "
            f"{safety_result.recommended_action}"
        )
        
        # Clear "relevant_red_flags_absent" if we found concerns
        if 'relevant_red_flags_absent' in context:
            context['relevant_red_flags_absent'] = None
    else:
        # Record that we checked and found no red flags
        context['relevant_red_flags_absent'] = ["No red flags identified in initial symptom assessment"]
    
    # Update conversation state and return
    conversation_state['context'] = context
    return conversation_state


"""
Example 2: Scout Agent Safety Analysis

The Scout agent reviews Host's findings and performs deeper analysis.
"""
def scout_agent_safety_analysis(conversation_state, detailed_symptoms, possible_conditions):
    """
    Example Scout agent safety analysis function.
    
    Args:
        conversation_state: The current conversation state
        detailed_symptoms: Detailed symptom information
        possible_conditions: Conditions being considered
        
    Returns:
        Updated conversation state with enhanced safety analysis
    """
    # Get current context
    context = conversation_state.get('context', {})
    
    # Combine symptoms and conditions for a more thorough safety check
    combined_query = f"Symptoms: {detailed_symptoms}\nConditions Being Considered: {possible_conditions}"
    
    # Perform more detailed safety check with possible conditions
    safety_result = safety_service.check_safety(
        symptoms=combined_query,
        similarity_threshold=0.5  # Lower threshold for higher sensitivity
    )
    
    # Get current safety concerns if any
    safety_concerns = context.get('safety_concerns', [])
    existing_ids = [concern['id'] for concern in safety_concerns]
    
    # Process any new concerns found
    for concern in safety_result.concerns:
        if concern.id in existing_ids:
            # Update existing concern with Scout's analysis
            for existing in safety_concerns:
                if existing['id'] == concern.id:
                    existing['agent_analysis'] += f"\n\nSCOUT ANALYSIS: Further evaluation indicates this {concern.category} is relevant to potential {possible_conditions}. Confidence: {concern.confidence:.2f}. {concern.clinical_pearls or ''}"
                    if "Scout" not in existing['reviewed_by']:
                        existing['reviewed_by'].append("Scout")
        else:
            # Add new concern found by Scout
            safety_concerns.append({
                'id': concern.id,
                'title': concern.title,
                'severity': concern.severity,
                'agent_analysis': f"SCOUT ANALYSIS: Identified {concern.category} related to potential {possible_conditions}. Confidence: {concern.confidence:.2f}. {concern.clinical_pearls or ''}",
                'assessment_status': "pending",
                'reviewed_by': ["Scout"]
            })
    
    # Update clinical assessment
    if safety_concerns:
        context['safety_concerns'] = safety_concerns
        
        # Update or create clinical assessment
        current_assessment = context.get('safety_clinical_assessment', '')
        scout_assessment = (
            f"SCOUT ASSESSMENT: Evaluated {len(safety_concerns)} safety concerns in context of possible conditions. "
            f"{'HIGH ALERT: ' if safety_result.highest_severity >= 4 else ''}"
            f"{safety_result.recommended_action}"
        )
        
        if current_assessment:
            context['safety_clinical_assessment'] = f"{current_assessment}\n\n{scout_assessment}"
        else:
            context['safety_clinical_assessment'] = scout_assessment
            
        # Clear "no red flags" if we found concerns
        if context.get('relevant_red_flags_absent'):
            context['relevant_red_flags_absent'] = None
    
    # Update conversation state and return
    conversation_state['context'] = context
    return conversation_state


"""
Example 3: PI Agent (Physician Investigator) Safety Validation

The PI agent performs expert analysis and validation of safety concerns.
"""
def pi_agent_safety_validation(conversation_state, differential_diagnosis):
    """
    Example PI agent safety validation function.
    
    Args:
        conversation_state: The current conversation state
        differential_diagnosis: Differential diagnosis information
        
    Returns:
        Updated conversation state with expert safety validation
    """
    # Get current context
    context = conversation_state.get('context', {})
    safety_concerns = context.get('safety_concerns', [])
    
    if not safety_concerns:
        # No concerns to validate
        return conversation_state
    
    # For each concern, add PI's expert validation
    for concern in safety_concerns:
        # Example clinical decision making by PI agent
        if concern['severity'] >= 4:
            # High severity concerns - mark for escalation
            concern['assessment_status'] = "escalated"
            concern['agent_analysis'] += "\n\nPI ANALYSIS: VALIDATED as high-priority safety concern requiring escalation. Based on clinical presentation and differential diagnosis, this requires urgent attention."
        elif concern['severity'] == 3:
            # Medium severity - clinical judgment
            concern['assessment_status'] = "reviewed"
            concern['agent_analysis'] += f"\n\nPI ANALYSIS: Clinical judgment indicates this is a valid concern requiring monitoring within the context of {differential_diagnosis}. Would recommend healthcare provider follow-up."
        else:
            # Lower severity - may clear if appropriate
            concern['assessment_status'] = "cleared"
            concern['agent_analysis'] += "\n\nPI ANALYSIS: After clinical review, this concern presents minimal risk in this specific context and can be managed with appropriate guidance and safety netting advice."
        
        # Add PI to reviewers
        if "PI" not in concern['reviewed_by']:
            concern['reviewed_by'].append("PI")
    
    # Update clinical assessment with PI's expert opinion
    current_assessment = context.get('safety_clinical_assessment', '')
    
    # Count concerns by status
    escalated = sum(1 for c in safety_concerns if c['assessment_status'] == "escalated")
    reviewed = sum(1 for c in safety_concerns if c['assessment_status'] == "reviewed")
    cleared = sum(1 for c in safety_concerns if c['assessment_status'] == "cleared")
    
    pi_assessment = (
        f"PI EXPERT ASSESSMENT: Completed clinical validation of {len(safety_concerns)} safety concerns. "
        f"Found {escalated} requiring urgent escalation, {reviewed} requiring healthcare provider review, "
        f"and {cleared} that can be managed with appropriate guidance. "
        f"{'RECOMMENDATION: Urgent medical attention advised. ' if escalated > 0 else 'RECOMMENDATION: '}"
        f"{'Standard healthcare provider follow-up advised. ' if escalated == 0 and reviewed > 0 else ''}"
        f"{'Appropriate for self-care with safety netting. ' if escalated == 0 and reviewed == 0 else ''}"
    )
    
    if current_assessment:
        context['safety_clinical_assessment'] = f"{current_assessment}\n\n{pi_assessment}"
    else:
        context['safety_clinical_assessment'] = pi_assessment
    
    # Update escalation advice based on PI's assessment
    if escalated > 0:
        context['escalation_advice'] = "Based on your symptoms, we recommend seeking urgent medical attention. Please contact emergency services or attend your nearest emergency department."
    elif reviewed > 0:
        context['escalation_advice'] = "Based on your symptoms, we recommend discussing with a healthcare provider. Please arrange an appointment with your doctor within the next few days."
    else:
        context['escalation_advice'] = "Based on our assessment, self-care options may be appropriate. However, if symptoms worsen or new symptoms develop, please consult a healthcare provider."
    
    # Update conversation state and return
    conversation_state['context'] = context
    return conversation_state


"""
Example 4: Medication Safety Check (for OTC recommendations)

Check if specific medications are safe given the user's symptoms and context.
"""
def check_medication_safety(conversation_state, medication):
    """
    Example medication safety check function.
    
    Args:
        conversation_state: The current conversation state
        medication: Medication to check
        
    Returns:
        Tuple of (is_safe, safety_message)
    """
    # Get current context
    context = conversation_state.get('context', {})
    
    # Extract relevant information
    symptoms = context.get('symptoms', '')
    
    # Dummy demographics - in production you'd get this from the user
    demographics = {
        "age": "45-55",
        "gender": "female"
    }
    
    # Check medication safety
    is_safe, concerns = safety_service.check_medication_safety(
        medication=medication,
        symptoms=symptoms,
        demographics=demographics
    )
    
    # Generate safety message
    if is_safe:
        return True, f"{medication} appears to be appropriate for your reported symptoms."
    else:
        concern_titles = [c.title for c in concerns]
        return False, f"{medication} may not be suitable due to: {', '.join(concern_titles)}. Please consult a healthcare provider."
