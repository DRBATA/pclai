"""
Safety Knowledge Base - Core functionality for managing clinical safety information.

This module provides a comprehensive interface for interacting with the safety database,
including vector similarity search for red flags, signposting, and escalation advice.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
import openai
from supabase import create_client, Client

# Configure logging
logger = logging.getLogger(__name__)

class SafetyKnowledgeBase:
    """
    SafetyKnowledgeBase provides access to clinical safety information through
    vector similarity search, allowing agents to identify potential safety concerns
    based on user symptoms and reported conditions.
    """
    
    def __init__(self):
        """Initialize the Safety Knowledge Base with Supabase and OpenAI connections."""
        # Load environment variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate configuration
        if not all([self.supabase_url, self.supabase_key, self.openai_api_key]):
            logger.warning("Safety knowledge base missing configuration. Vector search will be unavailable.")
            self.is_configured = False
            return
            
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Initialize Supabase client
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            self.is_configured = True
            logger.info("Safety knowledge base initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize safety knowledge base: {e}")
            self.is_configured = False
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a vector embedding for the given text using OpenAI's embedding API.
        
        Args:
            text (str): The text to generate an embedding for
            
        Returns:
            List[float]: The vector embedding
        """
        if not self.is_configured:
            logger.error("Cannot generate embedding: Safety knowledge base not configured")
            return []
            
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def search_safety_concerns(
        self, 
        query: str, 
        threshold: float = 0.7,
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for safety concerns by vector similarity.
        
        Args:
            query (str): The query text to search for
            threshold (float): Minimum similarity threshold (0-1)
            limit (int): Maximum number of results to return
            category (str, optional): Filter by category (red_flag, signposting, escalation)
            
        Returns:
            List[Dict[str, Any]]: The matching safety concerns
        """
        if not self.is_configured:
            logger.error("Cannot search safety concerns: Safety knowledge base not configured")
            return []
            
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        try:
            # Call the vector search function in PostgreSQL
            result = self.supabase.rpc(
                "match_safety_items", 
                {
                    "query_embedding": query_embedding, 
                    "match_threshold": threshold, 
                    "match_count": limit,
                    "filter_category": category
                }   
            ).execute()
            
            if hasattr(result, 'data'):
                return result.data
            return []
        except Exception as e:
            logger.error(f"Error searching safety concerns: {e}")
            return []
    
    def get_tags_for_safety_item(self, safety_id: str) -> Dict[str, List[str]]:
        """
        Get all tags associated with a safety item.
        
        Args:
            safety_id (str): The safety item ID
            
        Returns:
            Dict[str, List[str]]: Dictionary of tag categories and their values
        """
        if not self.is_configured:
            logger.error("Cannot get tags: Safety knowledge base not configured")
            return {}
            
        try:
            result = self.supabase.table("safety_tags")\
                .select("tag_category, tag_value")\
                .eq("safety_id", safety_id)\
                .execute()
                
            tags: Dict[str, List[str]] = {}
            for tag in result.data:
                category = tag["tag_category"]
                value = tag["tag_value"]
                if category not in tags:
                    tags[category] = []
                tags[category].append(value)
            return tags
        except Exception as e:
            logger.error(f"Error getting tags: {e}")
            return {}
    
    def get_safety_item_by_id(self, safety_id: str) -> Dict[str, Any]:
        """
        Get a safety item by its ID.
        
        Args:
            safety_id (str): The safety item ID
            
        Returns:
            Dict[str, Any]: The safety item
        """
        if not self.is_configured:
            logger.error("Cannot get safety item: Safety knowledge base not configured")
            return {}
            
        try:
            result = self.supabase.table("safety_knowledge")\
                .select("*")\
                .eq("id", safety_id)\
                .execute()
                
            if result.data and len(result.data) > 0:
                item = result.data[0]
                # Load tags
                item["tags"] = self.get_tags_for_safety_item(safety_id)
                return item
            return {}
        except Exception as e:
            logger.error(f"Error getting safety item: {e}")
            return {}
    
    def add_safety_knowledge(
        self,
        category: str,
        subcategory: str, 
        title: str, 
        description: str, 
        severity: int,
        action: str, 
        timeframe: str, 
        triggers: List[str], 
        wellness_thresholds: Optional[Dict[str, Any]] = None,
        symptom_patterns: Optional[Dict[str, Any]] = None, 
        body_systems: Optional[List[str]] = None,
        population_specifics: Optional[Dict[str, Any]] = None, 
        evidence_level: Optional[str] = None, 
        source: Optional[str] = None,
        clinical_pearls: Optional[str] = None, 
        guideline_limitations: Optional[str] = None,
        contextual_interpretation: Optional[str] = None, 
        evidence_quality_notes: Optional[str] = None
    ) -> Optional[str]:
        """
        Add a safety knowledge item with its embedding to the database.
        
        Args:
            category (str): The category (red_flag, signposting, escalation)
            subcategory (str): The subcategory (cardiac, respiratory, etc.)
            title (str): Brief title of the safety item
            description (str): Full description of the safety item
            severity (int): Severity rating on 1-5 scale (5 being most severe)
            action (str): Recommended action (999, A&E, GP, etc.)
            timeframe (str): Urgency (immediate, 24h, monitor, etc.)
            triggers (List[str]): Symptom patterns that trigger this flag
            wellness_thresholds (Dict[str, Any], optional): Minimum wellness scores that trigger concerns
            symptom_patterns (Dict[str, Any], optional): Structured patterns of symptoms
            body_systems (List[str], optional): Relevant body systems
            population_specifics (Dict[str, Any], optional): Special considerations for different populations
            evidence_level (str, optional): Level of evidence supporting this guideline
            source (str, optional): Source of guidance (NICE, NHS, etc.)
            clinical_pearls (str, optional): Experienced-based insights
            guideline_limitations (str, optional): Known limitations of standard guidance
            contextual_interpretation (str, optional): How to interpret findings in context
            evidence_quality_notes (str, optional): Notes on strength/applicability of evidence
            
        Returns:
            Optional[str]: The ID of the created safety item, or None if creation failed
        """
        if not self.is_configured:
            logger.error("Cannot add safety knowledge: Safety knowledge base not configured")
            return None
            
        # Create text for embedding
        embedding_text = f"""
        Title: {title}
        Category: {category}
        Subcategory: {subcategory}
        Description: {description}
        Severity: {severity}/5
        Triggers: {', '.join(triggers)}
        Action: {action}
        Timeframe: {timeframe}
        Clinical Pearls: {clinical_pearls or ''}
        Context: {contextual_interpretation or ''}
        """
        
        # Generate embedding
        embedding = self.generate_embedding(embedding_text)
        if not embedding:
            logger.error("Failed to generate embedding. Safety knowledge not added.")
            return None
        
        # Prepare data for insertion
        data = {
            "category": category,
            "subcategory": subcategory,
            "title": title,
            "description": description,
            "severity": severity,
            "action": action,
            "timeframe": timeframe,
            "triggers": triggers,
            "wellness_thresholds": wellness_thresholds,
            "symptom_patterns": symptom_patterns,
            "body_systems": body_systems,
            "population_specifics": population_specifics,
            "evidence_level": evidence_level,
            "source": source,
            "clinical_pearls": clinical_pearls,
            "guideline_limitations": guideline_limitations,
            "contextual_interpretation": contextual_interpretation,
            "evidence_quality_notes": evidence_quality_notes,
            "embedding": embedding
        }
        
        try:
            # Insert into database using Supabase client
            result = self.supabase.table("safety_knowledge").insert(data).execute()
            safety_id = result.data[0]["id"]
            logger.info(f"Added safety knowledge item with ID: {safety_id}")
            return safety_id
        except Exception as e:
            logger.error(f"Error adding safety knowledge: {e}")
            return None
    
    def add_safety_tags(self, safety_id: str, tags: Dict[str, Union[str, List[str]]]) -> bool:
        """
        Add tags to a safety knowledge item.
        
        Args:
            safety_id (str): The safety item ID
            tags (Dict[str, Union[str, List[str]]]): Dictionary of tag categories and their values
                Example: {"system": ["cardiovascular"], "population": "elderly"}
                
        Returns:
            bool: Whether the operation was successful
        """
        if not self.is_configured:
            logger.error("Cannot add safety tags: Safety knowledge base not configured")
            return False
            
        tag_data = []
        for tag_category, tag_values in tags.items():
            if isinstance(tag_values, list):
                for value in tag_values:
                    tag_data.append({
                        "safety_id": safety_id,
                        "tag_category": tag_category,
                        "tag_value": value
                    })
            else:
                tag_data.append({
                    "safety_id": safety_id,
                    "tag_category": tag_category,
                    "tag_value": tag_values
                })
        
        if not tag_data:
            return True
            
        try:
            self.supabase.table("safety_tags").insert(tag_data).execute()
            logger.info(f"Added {len(tag_data)} tags for safety item {safety_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding tags: {e}")
            return False


# Create the PostgreSQL function for vector search if it doesn't exist
def create_vector_search_function(supabase: Client) -> bool:
    """
    Create a PostgreSQL function for vector similarity search.
    
    Args:
        supabase (Client): The Supabase client
        
    Returns:
        bool: Whether the operation was successful
    """
    try:
        # SQL to create the function - needs to be run only once
        supabase.rpc(
            "exec_sql",
            {
                "sql_statement": """
                CREATE OR REPLACE FUNCTION match_safety_items(
                    query_embedding vector(1536),
                    match_threshold float,
                    match_count int,
                    filter_category text DEFAULT NULL
                ) RETURNS TABLE (
                    id uuid,
                    category text,
                    title text,
                    description text,
                    severity int,
                    action text,
                    timeframe text,
                    clinical_pearls text,
                    similarity float
                )
                LANGUAGE plpgsql
                AS $$
                BEGIN
                    RETURN QUERY
                    SELECT
                        safety_knowledge.id,
                        safety_knowledge.category,
                        safety_knowledge.title,
                        safety_knowledge.description,
                        safety_knowledge.severity,
                        safety_knowledge.action,
                        safety_knowledge.timeframe,
                        safety_knowledge.clinical_pearls,
                        1 - (safety_knowledge.embedding <=> query_embedding) as similarity
                    FROM safety_knowledge
                    WHERE 
                        (filter_category IS NULL OR safety_knowledge.category = filter_category) AND
                        (1 - (safety_knowledge.embedding <=> query_embedding)) > match_threshold
                    ORDER BY safety_knowledge.embedding <=> query_embedding
                    LIMIT match_count;
                END;
                $$;
                """
            }
        ).execute()
        logger.info("Vector search function created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating vector search function: {e}")
        return False


# Initialize safety knowledge base singleton
safety_kb = SafetyKnowledgeBase()
