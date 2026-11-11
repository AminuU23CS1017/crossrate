-- SP-050 PostgreSQL schema. Equivalent to app/database.py.
CREATE TABLE IF NOT EXISTS cached_responses (
    key VARCHAR(300) PRIMARY KEY,
    payload TEXT NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL
);
-- Recommended operational cleanup (choose retention policy before scheduling):
-- DELETE FROM cached_responses WHERE fetched_at < NOW() - INTERVAL '30 days';
