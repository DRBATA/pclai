-- Safety Knowledge Base Tables and Indexes
-- This SQL script creates the necessary tables for the clinical safety knowledge base.

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Safety Knowledge Table - Main table for safety information
CREATE TABLE IF NOT EXISTS safety_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL CHECK (category IN ('red_flag', 'signposting', 'escalation')),
    subcategory TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    action TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    triggers TEXT[] NOT NULL,
    wellness_thresholds JSONB,
    symptom_patterns JSONB,
    body_systems TEXT[],
    population_specifics JSONB,
    evidence_level TEXT,
    source TEXT,
    clinical_pearls TEXT,
    guideline_limitations TEXT,
    contextual_interpretation TEXT,
    evidence_quality_notes TEXT,
    embedding vector(1536) NOT NULL,
    search_text TSVECTOR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Safety Tags Table - For flexible tagging of safety items
CREATE TABLE IF NOT EXISTS safety_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    safety_id UUID NOT NULL REFERENCES safety_knowledge(id) ON DELETE CASCADE,
    tag_category TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    UNIQUE (safety_id, tag_category, tag_value)
);

-- Create a trigger function to update search_text on insert or update
CREATE OR REPLACE FUNCTION update_safety_search_text()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_text := to_tsvector('english', 
        coalesce(NEW.title, '') || ' ' || 
        coalesce(NEW.category, '') || ' ' || 
        coalesce(NEW.subcategory, '') || ' ' || 
        coalesce(NEW.description, '') || ' ' || 
        coalesce(NEW.action, '') || ' ' || 
        coalesce(NEW.timeframe, '') || ' ' || 
        coalesce(array_to_string(NEW.triggers, ' '), '') || ' ' || 
        coalesce(NEW.clinical_pearls, '') || ' ' || 
        coalesce(NEW.contextual_interpretation, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update search text on insert or update
DROP TRIGGER IF EXISTS update_safety_search_text_trigger ON safety_knowledge;
CREATE TRIGGER update_safety_search_text_trigger
BEFORE INSERT OR UPDATE ON safety_knowledge
FOR EACH ROW
EXECUTE PROCEDURE update_safety_search_text();

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at on update
DROP TRIGGER IF EXISTS update_safety_knowledge_updated_at ON safety_knowledge;
CREATE TRIGGER update_safety_knowledge_updated_at
BEFORE UPDATE ON safety_knowledge
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

-- Create IVFFlat index for fast vector similarity search
CREATE INDEX IF NOT EXISTS safety_knowledge_embedding_idx 
ON safety_knowledge 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create index on search_text for faster text search
CREATE INDEX IF NOT EXISTS safety_knowledge_search_text_idx 
ON safety_knowledge 
USING GIN (search_text);

-- Create indexes on commonly queried fields
CREATE INDEX IF NOT EXISTS safety_knowledge_category_idx ON safety_knowledge (category);
CREATE INDEX IF NOT EXISTS safety_knowledge_severity_idx ON safety_knowledge (severity);
CREATE INDEX IF NOT EXISTS safety_tags_safety_id_idx ON safety_tags (safety_id);
CREATE INDEX IF NOT EXISTS safety_tags_category_value_idx ON safety_tags (tag_category, tag_value);

-- Create vector similarity search function
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
