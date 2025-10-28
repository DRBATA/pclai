-- Safety Knowledge Base Tables for Supabase with pgvector
-- This version is adapted specifically for Supabase's vector implementation

-- Safety Knowledge Base Table
CREATE TABLE IF NOT EXISTS safety_knowledge (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    category text NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    severity int NOT NULL,
    action text,
    timeframe text,
    clinical_pearls text,
    embedding vector(1536),  -- OpenAI's text-embedding-ada-002 dimensions
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Safety Tags Table for categorization
CREATE TABLE IF NOT EXISTS safety_tags (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    safety_knowledge_id uuid NOT NULL REFERENCES safety_knowledge(id) ON DELETE CASCADE,
    tag text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);

-- After tables are created, now create the indexes

-- Create index on safety_tags for quick tag lookups 
-- (Now this will work because the 'tag' column exists)
CREATE INDEX IF NOT EXISTS idx_safety_tags_tag ON safety_tags(tag);

-- Create text search index on safety_knowledge
CREATE INDEX IF NOT EXISTS idx_safety_knowledge_text_search ON safety_knowledge
USING gin(to_tsvector('english', title || ' ' || description));

-- Create index on category for filtering
CREATE INDEX IF NOT EXISTS idx_safety_knowledge_category ON safety_knowledge(category);

-- Create vector similarity search index (IVFFlat for larger datasets)
CREATE INDEX IF NOT EXISTS safety_knowledge_embedding_idx ON safety_knowledge 
USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Function to match safety items using vector similarity
CREATE OR REPLACE FUNCTION match_safety_items(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.55,
    match_count int DEFAULT 10,
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
) LANGUAGE plpgsql AS $$
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
