"""
Safety Knowledge Base module for clinical OTC advisories.
Provides vector search capabilities for red flags, signposting, and escalation.
"""

from .knowledge_base import SafetyKnowledgeBase
from .safety_service import SafetyService

__all__ = ["SafetyKnowledgeBase", "SafetyService"]
