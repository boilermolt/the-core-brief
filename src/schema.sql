-- The Core Brief - Story Database Schema
-- SQLite database for tracking stories, topics, sources, and coverage over time

-- Core stories table
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    category TEXT NOT NULL,  -- regulatory, industry_news, research, community
    published_date TEXT,     -- ISO 8601 format
    fetched_date TEXT NOT NULL,
    summary TEXT,
    content TEXT,            -- Full scraped content if available
    relevance_score REAL DEFAULT 0.0,
    coverage_status TEXT DEFAULT 'discovered',  -- discovered, covered, monitoring, archived
    edition_date TEXT,       -- Which edition covered this (if any)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Topics/themes extracted from stories
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,           -- regulation, technology, safety, policy, incident, etc.
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many relationship: stories <-> topics
CREATE TABLE IF NOT EXISTS story_topics (
    story_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    relevance REAL DEFAULT 1.0,  -- How central is this topic to the story?
    PRIMARY KEY (story_id, topic_id),
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Keywords extracted from stories
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 1,
    first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
    last_seen TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many: stories <-> keywords
CREATE TABLE IF NOT EXISTS story_keywords (
    story_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,
    PRIMARY KEY (story_id, keyword_id),
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE
);

-- Newsletter editions
CREATE TABLE IF NOT EXISTS editions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edition_date TEXT UNIQUE NOT NULL,
    edition_type TEXT DEFAULT 'weekly',  -- weekly, monthly-deep-dive
    title TEXT,
    published BOOLEAN DEFAULT 0,
    substack_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    published_at TEXT
);

-- Stories featured in editions
CREATE TABLE IF NOT EXISTS edition_stories (
    edition_id INTEGER NOT NULL,
    story_id INTEGER NOT NULL,
    position INTEGER,         -- Order in the edition
    section TEXT,             -- top-stories, in-brief, what-to-watch
    PRIMARY KEY (edition_id, story_id),
    FOREIGN KEY (edition_id) REFERENCES editions(id) ON DELETE CASCADE,
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
);

-- Deep dive topic tracking
CREATE TABLE IF NOT EXISTS deep_dive_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    priority INTEGER DEFAULT 0,
    rationale TEXT,
    story_count INTEGER DEFAULT 0,  -- How many stories mention this topic?
    last_coverage_date TEXT,
    status TEXT DEFAULT 'proposed',  -- proposed, researching, drafted, published
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Follow-up tracking (stories that need monitoring)
CREATE TABLE IF NOT EXISTS follow_ups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    follow_up_type TEXT,      -- regulatory-action, incident-update, project-milestone
    expected_date TEXT,
    notes TEXT,
    resolved BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_stories_category ON stories(category);
CREATE INDEX IF NOT EXISTS idx_stories_published_date ON stories(published_date);
CREATE INDEX IF NOT EXISTS idx_stories_coverage_status ON stories(coverage_status);
CREATE INDEX IF NOT EXISTS idx_stories_edition_date ON stories(edition_date);
CREATE INDEX IF NOT EXISTS idx_topics_category ON topics(category);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);

-- Views for analytics

-- Topic frequency across all stories
CREATE VIEW IF NOT EXISTS v_topic_frequency AS
SELECT 
    t.id,
    t.name,
    t.category,
    COUNT(st.story_id) as story_count,
    AVG(st.relevance) as avg_relevance,
    MAX(s.published_date) as last_story_date
FROM topics t
LEFT JOIN story_topics st ON t.id = st.topic_id
LEFT JOIN stories s ON st.story_id = s.id
GROUP BY t.id;

-- Trending topics (last 30 days)
CREATE VIEW IF NOT EXISTS v_trending_topics AS
SELECT 
    t.id,
    t.name,
    t.category,
    COUNT(st.story_id) as recent_story_count,
    AVG(s.relevance_score) as avg_relevance_score
FROM topics t
LEFT JOIN story_topics st ON t.id = st.topic_id
LEFT JOIN stories s ON st.story_id = s.id
WHERE s.published_date >= date('now', '-30 days')
GROUP BY t.id
ORDER BY recent_story_count DESC, avg_relevance_score DESC;

-- Coverage gaps (discovered stories not yet covered)
CREATE VIEW IF NOT EXISTS v_coverage_queue AS
SELECT 
    s.id,
    s.title,
    s.source,
    s.category,
    s.published_date,
    s.relevance_score,
    GROUP_CONCAT(t.name, ', ') as topics
FROM stories s
LEFT JOIN story_topics st ON s.id = st.story_id
LEFT JOIN topics t ON st.topic_id = t.id
WHERE s.coverage_status = 'discovered'
GROUP BY s.id
ORDER BY s.relevance_score DESC, s.published_date DESC;
