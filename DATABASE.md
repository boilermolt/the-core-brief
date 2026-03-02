# The Core Brief - Story Database

SQLite database for tracking stories, topics, and coverage over time.

## Purpose

The story database enables:
- **Story tracking** across sources and time
- **Topic extraction** and trend analysis
- **Deep dive planning** based on recurring themes
- **Coverage management** (what's been published, what's pending)
- **Follow-up reminders** for developing stories

---

## Schema Overview

### Core Tables

**`stories`** - All discovered stories
- URL, title, source, category, published date
- Summary, full content (if scraped)
- Relevance score, coverage status
- Edition coverage tracking

**`topics`** - Extracted themes (NRC Oversight, Advanced Reactors, etc.)
- Name, category, description
- Automatically extracted via keyword rules

**`keywords`** - Individual keywords from stories
- Frequency tracking, first/last seen

**`editions`** - Newsletter editions
- Edition date, type (weekly/monthly), publish status
- Substack URL when published

**`deep_dive_candidates`** - Topics worthy of long-form coverage
- Priority, rationale, story count
- Status tracking (proposed → researching → drafted → published)

**`follow_ups`** - Stories needing future monitoring
- Type (regulatory-action, incident-update, project-milestone)
- Expected date, resolution status

### Relationships

- `story_topics` - Many-to-many: stories ↔ topics (with relevance score)
- `story_keywords` - Many-to-many: stories ↔ keywords
- `edition_stories` - Stories featured in editions (with position/section)

---

## CLI Usage

### Import aggregator data
```bash
python src/import_aggregator_to_db.py
```

### View database stats
```bash
python src/story_db.py stats
```

### Trending topics (last 30 days)
```bash
python src/story_db.py trending
```

### Deep dive candidates (3+ stories)
```bash
python src/story_db.py candidates
```

### Uncovered stories (not yet published)
```bash
python src/story_db.py uncovered
```

### Pending follow-ups
```bash
python src/story_db.py follow-ups
```

---

## Python API

```python
from story_db import StoryDB, Story, Topic

db = StoryDB()

# Add a story
story = Story(
    url="https://example.com/story",
    title="New Reactor Design Approved",
    source="Nuclear News",
    category="industry_news",
    published_date="2026-03-01",
    summary="NRC approves...",
    relevance_score=2.5,
    keywords=["NRC", "license", "SMR"]
)
story_id = db.add_story(story)

# Add a topic
topic = Topic(name="SMR Licensing", category="regulation")
topic_id = db.add_topic(topic)

# Link story to topic
db.link_story_topic(story_id, topic_id, relevance=1.0)

# Get trending topics
trending = db.get_trending_topics(days=30, limit=10)

# Get deep dive candidates
candidates = db.get_deep_dive_candidates(min_stories=3)

# Mark story as covered
db.mark_covered(story_id, edition_date="2026-03-02", section="top-stories")

# Add follow-up reminder
db.add_follow_up(
    story_id=story_id,
    follow_up_type="regulatory-action",
    expected_date="2026-04-15",
    notes="NRC comment period closes"
)
```

---

## Topic Classification

Stories are automatically tagged with topics based on keyword matching:

| Topic | Keywords | Category |
|-------|----------|----------|
| NRC Oversight | nrc, reactor oversight, rop, inspection | regulation |
| Advanced Reactors | smr, gen iv, advanced reactor | technology |
| Radiation Safety | radiation, dose, alara, exposure | safety |
| Security | security, force-on-force, cybersecurity | security |
| Licensing | license, licensing, construction permit | regulation |
| Spent Fuel | spent fuel, dry cask, repository, waste | waste-management |
| TRISO Fuel | triso, pebble fuel, coated particle | technology |
| Molten Salt Reactors | molten salt, fhr, fluoride salt | technology |
| Decommissioning | decommissioning, decontamination | operations |
| New Build | construction, new build, vogtle | projects |
| Incidents | incident, event, leak, spill | safety |
| IAEA | iaea, international atomic energy | international |

Extend topic rules in `src/import_aggregator_to_db.py`.

---

## Views for Analytics

**`v_topic_frequency`** - Topic occurrence across all stories

**`v_trending_topics`** - Hot topics (last 30 days)

**`v_coverage_queue`** - Uncovered stories ranked by relevance

---

## Workflow Integration

1. **Weekly aggregation run** → generates `data/cache/fetch_*.json`
2. **Import to database** → `python src/import_aggregator_to_db.py`
3. **Review trends** → `python src/story_db.py trending`
4. **Pick stories for edition** → `python src/story_db.py uncovered`
5. **Draft edition** → Write weekly digest
6. **Mark covered** → Update coverage status in DB
7. **Monthly deep dive planning** → `python src/story_db.py candidates`

---

## Database Location

`data/stories.db` (SQLite, gitignored)

Schema: `src/schema.sql`  
Manager: `src/story_db.py`  
Importer: `src/import_aggregator_to_db.py`
