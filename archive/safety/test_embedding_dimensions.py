"""
Embedding Dimension Verification Script

This script tests the output dimension of GPT-4.1 Nano embeddings
to ensure compatibility with our database schema (1536 dimensions).
"""
import os
import logging
import sys
from dotenv import load_dotenv
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_embedding_dimensions():
    """Test the dimension size of GPT-4.1 Nano embeddings."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    client = openai.OpenAI(api_key=openai_api_key)
    
    # Test text (representing a clinical safety item)
    test_text = "Patient presenting with sudden onset severe headache, described as worst headache of life, with accompanying nausea and photophobia."
    
    logger.info("Testing embedding dimensions for GPT-4.1 Nano...")
    
    try:
        # Test the new model
        response = client.embeddings.create(
            model="gpt-4.1-nano",
            input=test_text
        )
        new_embedding = response.data[0].embedding
        new_dim = len(new_embedding)
        
        logger.info(f"GPT-4.1 Nano embedding dimension: {new_dim}")
        
        # Also test the original model for comparison
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=test_text
        )
        orig_embedding = response.data[0].embedding
        orig_dim = len(orig_embedding)
        
        logger.info(f"Original embedding (text-embedding-ada-002) dimension: {orig_dim}")
        
        if new_dim == 1536:
            logger.info("✓ COMPATIBLE: GPT-4.1 Nano produces 1536-dimension vectors, matching your database schema.")
            logger.info("You can safely proceed with the new model.")
            return True
        else:
            logger.warning(f"⚠ INCOMPATIBLE: GPT-4.1 Nano produces {new_dim}-dimension vectors, but your database expects 1536!")
            logger.warning("Database schema updates will be required before proceeding.")
            return False
            
    except Exception as e:
        logger.error(f"Error testing embedding dimensions: {e}")
        return False
        
if __name__ == "__main__":
    is_compatible = test_embedding_dimensions()
    # Exit with error code if dimensions are incompatible
    if not is_compatible:
        sys.exit(1)
