"""
Safety Service - Clinical safety checking service for OTC medication agents.

This module provides a high-level interface for agents to check for safety concerns
based on reported symptoms, demographics, and clinical context.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel

from .knowledge_base import safety_kb

# Configure logging
logger = logging.getLogger(__name__)

class SafetyConcern(BaseModel):
    """
    Represents a safety concern identified during safety checking.
    """
    id: str
    category: str
    title: str
    severity: int
    action: str
    timeframe: str
    description: str
    confidence: float
    clinical_pearls: Optional[str] = None
    tags: Optional[Dict[str, List[str]]] = None
    agent_analysis: Optional[str] = None  # Agent's reasoning about this concern
    assessment_status: Optional[str] = None  # e.g., 'pending', 'reviewed', 'cleared', 'escalated'

class SafetyCheckResult(BaseModel):
    """
    Result of a safety check operation.
    """
    concerns: List[SafetyConcern]
    has_red_flags: bool
    highest_severity: int
    urgent_escalation_needed: bool
    recommended_action: str
    raw_query: str
    clinical_assessment: Optional[str] = None  # Overall clinical assessment
    reviewed_by: Optional[List[str]] = None  # List of agents who reviewed

class SafetyService:
    """
    SafetyService provides clinical safety checking capabilities to agents,
    enabling identification of red flags, appropriate signposting, and
    escalation advice based on reported symptoms and user context.
    """
    
    def __init__(self):
        """Initialize the Safety Service."""
        self.knowledge_base = safety_kb
    
    def check_safety(
        self,
        symptoms: str,
        demographics: Optional[Dict[str, Any]] = None,
        medical_history: Optional[str] = None,
        current_medications: Optional[List[str]] = None,
        wellness_scores: Optional[Dict[str, float]] = None,
        similarity_threshold: float = 0.55
    ) -> SafetyCheckResult:
        """
        Check for safety concerns based on symptoms and context.
        
        Args:
            symptoms (str): Reported symptoms from the user
            demographics (Dict[str, Any], optional): User demographics (age, sex, etc.)
            medical_history (str, optional): Relevant medical history
            current_medications (List[str], optional): Current medications
            wellness_scores (Dict[str, float], optional): Current wellness scores
            similarity_threshold (float): Minimum similarity threshold (0-1)
            
        Returns:
            SafetyCheckResult: The safety check result with identified concerns
        """
        # Create comprehensive query for vector search
        query_parts = [f"Symptoms: {symptoms}"]
        
        if demographics:
            demo_str = ", ".join([f"{k}: {v}" for k, v in demographics.items()])
            query_parts.append(f"Demographics: {demo_str}")
            
        if medical_history:
            query_parts.append(f"History: {medical_history}")
            
        if current_medications:
            query_parts.append(f"Medications: {', '.join(current_medications)}")
        
        query = " | ".join(query_parts)
        logger.info(f"Running safety check for: {query}")
        
        # Search for potential concerns (red flags, signposting advice, escalation)
        all_concerns = []
        
        # First check for red flags (highest priority)
        red_flags = self.knowledge_base.search_safety_concerns(
            query, 
            threshold=similarity_threshold,
            limit=10, 
            category="red_flag"
        )
        
        # Then check for signposting advice
        signposting = self.knowledge_base.search_safety_concerns(
            query, 
            threshold=similarity_threshold,
            limit=6, 
            category="signposting"
        )
        
        # Finally check for escalation advice
        escalation = self.knowledge_base.search_safety_concerns(
            query, 
            threshold=similarity_threshold,
            limit=4, 
            category="escalation"
        )
        
        # Process results
        concerns = []
        highest_severity = 0
        has_red_flags = False
        urgent_escalation_needed = False
        
        # Process red flags
        for flag in red_flags:
            concern = SafetyConcern(
                id=flag["id"],
                category=flag["category"],
                title=flag["title"],
                severity=flag["severity"],
                action=flag["action"],
                timeframe=flag["timeframe"],
                description=flag["description"],
                confidence=flag["similarity"],
                clinical_pearls=flag.get("clinical_pearls")
            )
            
            # Get tags if available
            tags = self.knowledge_base.get_tags_for_safety_item(flag["id"])
            if tags:
                concern.tags = tags
                
            concerns.append(concern)
            highest_severity = max(highest_severity, flag["severity"])
            has_red_flags = True
            
            # Check if this needs urgent escalation (severity 4-5)
            if flag["severity"] >= 4:
                urgent_escalation_needed = True
        
        # Process signposting and escalation
        for item in signposting + escalation:
            concern = SafetyConcern(
                id=item["id"],
                category=item["category"],
                title=item["title"],
                severity=item["severity"],
                action=item["action"],
                timeframe=item["timeframe"],
                description=item["description"],
                confidence=item["similarity"],
                clinical_pearls=item.get("clinical_pearls")
            )
            
            # Get tags if available
            tags = self.knowledge_base.get_tags_for_safety_item(item["id"])
            if tags:
                concern.tags = tags
                
            concerns.append(concern)
            highest_severity = max(highest_severity, item["severity"])
        
        # Determine recommended action based on highest severity
        recommended_action = self._get_recommended_action(highest_severity, urgent_escalation_needed)
        
        return SafetyCheckResult(
            concerns=concerns,
            has_red_flags=has_red_flags,
            highest_severity=highest_severity,
            urgent_escalation_needed=urgent_escalation_needed,
            recommended_action=recommended_action,
            raw_query=query
        )
    
    def _get_recommended_action(self, severity: int, urgent_escalation: bool) -> str:
        """
        Get recommended action based on severity level.
        
        Args:
            severity (int): Highest severity level found
            urgent_escalation (bool): Whether urgent escalation is needed
            
        Returns:
            str: Recommended action advice
        """
        if urgent_escalation:
            return "URGENT: Recommend immediate professional medical attention."
            
        if severity == 5:
            return "EMERGENCY: Call 999 or go to A&E immediately."
        elif severity == 4:
            return "URGENT: Seek same-day emergency care."
        elif severity == 3:
            return "Advise seeing GP within 24-48 hours."
        elif severity == 2:
            return "Advise consulting with a pharmacist."
        else:
            return "Self-care appropriate with standard precautions."
    
    def check_medication_safety(
        self,
        medication: str,
        symptoms: str,
        demographics: Optional[Dict[str, Any]] = None,
        medical_history: Optional[str] = None,
        current_medications: Optional[List[str]] = None,
        similarity_threshold: float = 0.65
    ) -> Tuple[bool, List[SafetyConcern]]:
        """
        Check if a medication is safe given the user's symptoms and context.
        
        Args:
            medication (str): The medication to check
            symptoms (str): Reported symptoms
            demographics (Dict[str, Any], optional): User demographics
            medical_history (str, optional): Relevant medical history
            current_medications (List[str], optional): Current medications
            similarity_threshold (float): Minimum similarity threshold (0-1)
            
        Returns:
            Tuple[bool, List[SafetyConcern]]: Whether the medication is safe and any concerns
        """
        # Create medication safety query
        query_parts = [
            f"Medication: {medication}",
            f"Symptoms: {symptoms}"
        ]
        
        if demographics:
            demo_str = ", ".join([f"{k}: {v}" for k, v in demographics.items()])
            query_parts.append(f"Demographics: {demo_str}")
            
        if medical_history:
            query_parts.append(f"History: {medical_history}")
            
        if current_medications:
            query_parts.append(f"Medications: {', '.join(current_medications)}")
        
        query = " | ".join(query_parts)
        logger.info(f"Running medication safety check for: {query}")
        
        # Search for potential medication concerns
        concerns_data = self.knowledge_base.search_safety_concerns(
            query, 
            threshold=similarity_threshold,
            limit=5
        )
        
        if not concerns_data:
            return True, []
            
        # Process concerns
        concerns = []
        is_safe = True
        
        for item in concerns_data:
            concern = SafetyConcern(
                id=item["id"],
                category=item["category"],
                title=item["title"],
                severity=item["severity"],
                action=item["action"],
                timeframe=item["timeframe"],
                description=item["description"],
                confidence=item["similarity"],
                clinical_pearls=item.get("clinical_pearls")
            )
            
            # Get tags if available
            tags = self.knowledge_base.get_tags_for_safety_item(item["id"])
            if tags:
                concern.tags = tags
                
            concerns.append(concern)
            
            # If any high severity concerns, medication might not be safe
            # Lower similarity threshold for medication safety determinations
            if item["severity"] >= 3 and item["similarity"] >= 0.65:
                is_safe = False
        
        return is_safe, concerns


# Create safety service singleton
safety_service = SafetyService()
