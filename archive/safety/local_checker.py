"""
Local Red Flag Checker - Simple keyword-based safety detection
Uses local JSON file for fast, deterministic red flag detection
"""
import json
import os
from typing import Dict, List, Any

class LocalRedFlagChecker:
    """Simple keyword-based red flag detection using local JSON"""
    
    def __init__(self):
        """Load red flags from local JSON file"""
        json_path = os.path.join(os.path.dirname(__file__), "red_flags.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.red_flags = data["red_flags"]
    
    def check(self, symptoms_text: str, age: int = None) -> Dict[str, Any]:
        """
        Check symptoms against red flag triggers
        
        Args:
            symptoms_text: Description of symptoms (will be lowercased)
            age: Patient age (optional, used for child checks)
            
        Returns:
            Dict with red flag results
        """
        symptoms_lower = symptoms_text.lower()
        matched_flags = []
        
        # Check each red flag
        for flag in self.red_flags:
            # Special handling for pediatric flags
            if flag["category"] == "pediatric":
                if flag["id"] == "child_under_2" and age and age < 2:
                    matched_flags.append({
                        **flag,
                        "confidence": 1.0,
                        "matched_trigger": f"Child age {age} < 2 years"
                    })
                    continue
            
            # Check if any trigger phrase is present
            for trigger in flag["triggers"]:
                if trigger.lower() in symptoms_lower:
                    matched_flags.append({
                        **flag,
                        "confidence": 1.0,
                        "matched_trigger": trigger
                    })
                    break  # Only count each flag once
        
        # Sort by severity (highest first)
        matched_flags.sort(key=lambda x: x["severity"], reverse=True)
        
        highest_severity = max([f["severity"] for f in matched_flags], default=0)
        
        return {
            "has_red_flags": len(matched_flags) > 0,
            "highest_severity": highest_severity,
            "urgent_escalation_needed": highest_severity >= 5,
            "recommended_action": self._get_action(highest_severity),
            "concerns_found": len(matched_flags),
            "concerns": matched_flags[:5]  # Top 5
        }
    
    def _get_action(self, severity: int) -> str:
        """Get recommended action based on severity"""
        if severity >= 5:
            return "EMERGENCY: Call 999 immediately"
        elif severity == 4:
            return "URGENT: Go to A&E or call 999"
        elif severity == 3:
            return "Seek GP review within 24 hours"
        elif severity == 2:
            return "Consult pharmacist or GP when convenient"
        else:
            return "Self-care appropriate"


# Singleton instance
local_checker = LocalRedFlagChecker()
