#!/usr/bin/env python3
"""
The Core Brief - Story Database Manager
Manages SQLite database for story tracking, topic analysis, and deep dive planning.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

DB_PATH = Path(__file__).parent.parent / "data" / "stories.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


@dataclass
class Story:
    url: str
    title: str
    source: str
    category: str
    published_date: Optional[str]
    summary: str
    relevance_score: float
    keywords: List[str]
    id: Optional[int] = None


@dataclass
class Topic:
    name: str
    category: str
    description: Optional[str] = None
    id: Optional[int] = None


class StoryDB:
    """Manage The Core Brief story database."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            schema = SCHEMA_PATH.read_text()
            conn.executescript(schema)
    
    def add_story(self, story: Story) -> int:
        """Add a story to the database. Returns story ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert or update story
            cursor.execute("""
                INSERT INTO stories 
                (url, title, source, category, published_date, summary, relevance_score, fetched_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    summary=excluded.summary,
                    relevance_score=excluded.relevance_score,
                    updated_at=CURRENT_TIMESTAMP
            """, (
                story.url,
                story.title,
                story.source,
                story.category,
                story.published_date,
                story.summary,
                story.relevance_score,
                datetime.now().isoformat()
            ))
            
            # Get story ID
            cursor.execute("SELECT id FROM stories WHERE url = ?", (story.url,))
            story_id = cursor.fetchone()[0]
            
            # Add keywords
            for keyword in story.keywords:
                cursor.execute("""
                    INSERT INTO keywords (keyword) VALUES (?)
                    ON CONFLICT(keyword) DO UPDATE SET
                        frequency = frequency + 1,
                        last_seen = CURRENT_TIMESTAMP
                """, (keyword,))
                
                cursor.execute("SELECT id FROM keywords WHERE keyword = ?", (keyword,))
                keyword_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT OR IGNORE INTO story_keywords (story_id, keyword_id)
                    VALUES (?, ?)
                """, (story_id, keyword_id))
            
            conn.commit()
            return story_id
    
    def add_topic(self, topic: Topic) -> int:
        """Add a topic. Returns topic ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO topics (name, category, description)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    category=excluded.category,
                    description=excluded.description
            """, (topic.name, topic.category, topic.description))
            
            cursor.execute("SELECT id FROM topics WHERE name = ?", (topic.name,))
            return cursor.fetchone()[0]
    
    def link_story_topic(self, story_id: int, topic_id: int, relevance: float = 1.0):
        """Link a story to a topic."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO story_topics (story_id, topic_id, relevance)
                VALUES (?, ?, ?)
            """, (story_id, topic_id, relevance))
    
    def get_trending_topics(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get trending topics from the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.id,
                    t.name,
                    t.category,
                    COUNT(st.story_id) as story_count,
                    AVG(s.relevance_score) as avg_score
                FROM topics t
                JOIN story_topics st ON t.id = st.topic_id
                JOIN stories s ON st.story_id = s.id
                WHERE s.published_date >= date('now', ?)
                GROUP BY t.id
                ORDER BY story_count DESC, avg_score DESC
                LIMIT ?
            """, (f'-{days} days', limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_deep_dive_candidates(self, min_stories: int = 3) -> List[Dict]:
        """Get topics suitable for deep dive coverage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.id,
                    t.name,
                    t.category,
                    COUNT(st.story_id) as story_count,
                    MAX(s.published_date) as latest_story,
                    AVG(s.relevance_score) as avg_relevance
                FROM topics t
                JOIN story_topics st ON t.id = st.topic_id
                JOIN stories s ON st.story_id = s.id
                GROUP BY t.id
                HAVING story_count >= ?
                ORDER BY story_count DESC, avg_relevance DESC
            """, (min_stories,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_uncovered_stories(self, limit: int = 20) -> List[Dict]:
        """Get stories not yet covered in any edition."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id,
                    s.url,
                    s.title,
                    s.source,
                    s.category,
                    s.published_date,
                    s.relevance_score,
                    GROUP_CONCAT(k.keyword, ', ') as keywords
                FROM stories s
                LEFT JOIN story_keywords sk ON s.id = sk.story_id
                LEFT JOIN keywords k ON sk.keyword_id = k.id
                WHERE s.coverage_status = 'discovered'
                GROUP BY s.id
                ORDER BY s.relevance_score DESC, s.published_date DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_covered(self, story_id: int, edition_date: str, section: str = 'top-stories'):
        """Mark a story as covered in an edition."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE stories
                SET coverage_status = 'covered', edition_date = ?
                WHERE id = ?
            """, (edition_date, story_id))
    
    def add_follow_up(self, story_id: int, follow_up_type: str, expected_date: str, notes: str):
        """Add a follow-up reminder for a story."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO follow_ups (story_id, follow_up_type, expected_date, notes)
                VALUES (?, ?, ?, ?)
            """, (story_id, follow_up_type, expected_date, notes))
    
    def get_pending_follow_ups(self) -> List[Dict]:
        """Get unresolved follow-ups."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    f.id,
                    f.follow_up_type,
                    f.expected_date,
                    f.notes,
                    s.title as story_title,
                    s.url as story_url
                FROM follow_ups f
                JOIN stories s ON f.story_id = s.id
                WHERE f.resolved = 0
                ORDER BY f.expected_date
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def export_stats(self) -> Dict:
        """Export database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM stories")
            total_stories = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM stories WHERE coverage_status = 'covered'")
            covered_stories = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM topics")
            total_topics = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM keywords")
            total_keywords = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM follow_ups WHERE resolved = 0")
            pending_follow_ups = cursor.fetchone()[0]
            
            return {
                'total_stories': total_stories,
                'covered_stories': covered_stories,
                'uncovered_stories': total_stories - covered_stories,
                'total_topics': total_topics,
                'total_keywords': total_keywords,
                'pending_follow_ups': pending_follow_ups
            }


def main():
    """CLI for story database."""
    import sys
    
    db = StoryDB()
    
    if len(sys.argv) < 2:
        print("Usage: story_db.py [stats|trending|candidates|uncovered|follow-ups]")
        return 1
    
    command = sys.argv[1]
    
    if command == 'stats':
        stats = db.export_stats()
        print("\n📊 The Core Brief - Database Stats\n")
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    elif command == 'trending':
        topics = db.get_trending_topics(days=30, limit=10)
        print("\n🔥 Trending Topics (Last 30 Days)\n")
        for t in topics:
            print(f"  {t['name']} ({t['category']}): {t['story_count']} stories, avg score {t['avg_score']:.2f}")
    
    elif command == 'candidates':
        candidates = db.get_deep_dive_candidates(min_stories=3)
        print("\n📝 Deep Dive Candidates\n")
        for c in candidates:
            print(f"  {c['name']} ({c['category']}): {c['story_count']} stories, latest: {c['latest_story']}")
    
    elif command == 'uncovered':
        stories = db.get_uncovered_stories(limit=10)
        print("\n📰 Uncovered Stories (Top 10)\n")
        for s in stories:
            print(f"  [{s['source']}] {s['title']}")
            print(f"    Score: {s['relevance_score']:.2f} | Date: {s['published_date']}")
            print(f"    {s['url']}\n")
    
    elif command == 'follow-ups':
        follow_ups = db.get_pending_follow_ups()
        print("\n⏰ Pending Follow-Ups\n")
        for f in follow_ups:
            print(f"  {f['follow_up_type']} - Expected: {f['expected_date']}")
            print(f"    Story: {f['story_title']}")
            print(f"    Notes: {f['notes']}\n")
    
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    exit(main() or 0)
