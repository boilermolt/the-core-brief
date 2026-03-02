#!/usr/bin/env python3
"""
Import aggregator JSON cache files into the story database.
Also performs topic extraction and classification.
"""

import json
from pathlib import Path
from story_db import StoryDB, Story, Topic
from datetime import datetime
import re

# Topic classification rules
TOPIC_RULES = {
    'NRC Oversight': {
        'keywords': ['nrc', 'reactor oversight', 'rop', 'inspection'],
        'category': 'regulation'
    },
    'Advanced Reactors': {
        'keywords': ['smr', 'small modular reactor', 'gen iv', 'generation iv', 'advanced reactor'],
        'category': 'technology'
    },
    'Radiation Safety': {
        'keywords': ['radiation', 'dose', 'alara', 'exposure', 'contamination'],
        'category': 'safety'
    },
    'Security': {
        'keywords': ['security', 'force-on-force', 'fof', 'cybersecurity', 'safeguards'],
        'category': 'security'
    },
    'Licensing': {
        'keywords': ['license', 'licensing', 'construction permit', 'operating license'],
        'category': 'regulation'
    },
    'Spent Fuel': {
        'keywords': ['spent fuel', 'dry cask', 'repository', 'waste'],
        'category': 'waste-management'
    },
    'TRISO Fuel': {
        'keywords': ['triso', 'pebble fuel', 'coated particle'],
        'category': 'technology'
    },
    'Molten Salt Reactors': {
        'keywords': ['molten salt', 'fhr', 'fluoride salt', 'flibe'],
        'category': 'technology'
    },
    'Decommissioning': {
        'keywords': ['decommissioning', 'decontamination', 'plant closure'],
        'category': 'operations'
    },
    'New Build': {
        'keywords': ['construction', 'new build', 'vogtle', 'barakah'],
        'category': 'projects'
    },
    'Incidents': {
        'keywords': ['incident', 'event', 'leak', 'spill', 'uptake'],
        'category': 'safety'
    },
    'IAEA': {
        'keywords': ['iaea', 'international atomic energy agency'],
        'category': 'international'
    }
}


def extract_topics(text: str) -> list:
    """Extract topics from text based on keyword matching."""
    text_lower = text.lower()
    matched_topics = []
    
    for topic_name, rule in TOPIC_RULES.items():
        for keyword in rule['keywords']:
            if keyword in text_lower:
                matched_topics.append((topic_name, rule['category']))
                break
    
    return matched_topics


def import_cache_file(db: StoryDB, cache_path: Path):
    """Import a single aggregator cache file."""
    with open(cache_path) as f:
        data = json.load(f)
    
    print(f"\nImporting {cache_path.name}...")
    print(f"  Found {len(data['items'])} items")
    
    imported_count = 0
    for item in data['items']:
        # Create Story object
        story = Story(
            url=item['url'],
            title=item['title'],
            source=item['source'],
            category=item['category'],
            published_date=item.get('published'),
            summary=item.get('summary', ''),
            relevance_score=item.get('score', 0.0),
            keywords=item.get('keywords_matched', [])
        )
        
        # Add to database
        story_id = db.add_story(story)
        
        # Extract and add topics
        search_text = f"{story.title} {story.summary}"
        topics = extract_topics(search_text)
        
        for topic_name, topic_category in topics:
            topic = Topic(name=topic_name, category=topic_category)
            topic_id = db.add_topic(topic)
            db.link_story_topic(story_id, topic_id, relevance=1.0)
        
        imported_count += 1
    
    print(f"  ✓ Imported {imported_count} stories")


def main():
    """Import all cache files into the database."""
    db = StoryDB()
    
    cache_dir = Path(__file__).parent.parent / "data" / "cache"
    cache_files = sorted(cache_dir.glob("fetch_*.json"))
    
    if not cache_files:
        print("No cache files found to import.")
        return 1
    
    print(f"Found {len(cache_files)} cache file(s) to import")
    
    for cache_file in cache_files:
        import_cache_file(db, cache_file)
    
    print("\n" + "="*50)
    stats = db.export_stats()
    print("\n📊 Database Stats After Import:\n")
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n✓ Import complete")


if __name__ == "__main__":
    exit(main() or 0)
